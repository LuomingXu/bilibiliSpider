import json
import threading
import time
from typing import Set, List

import selfusepy
from selfusepy.url import HTTPResponse
from sqlalchemy.engine import ResultProxy

import _email
import _file
import _s3
from _user.DO import UserProfileDO
from _user.Entity import UserProfile
from config import DBSession, log, email_to_addr


def __main__(mids: Set[int]):
  session = DBSession()
  for i in mids:
    mid = {'mid': i}
    res: HTTPResponse = selfusepy.get('https://api.bilibili.com/x/space/acc/info', **mid)
    isUpdated: bool = False

    try:
      resData: UserProfile = selfusepy.parse_json(res.data, UserProfile())
      dbData: UserProfileDO = session.query(UserProfileDO).filter(UserProfileDO.mid == i).first()
      if dbData:  # 存在
        resDO: UserProfileDO = UserProfileDO(resData)
        for item in vars(dbData).items():
          """
          将获取到的信息与db中的数据进行对比更新
          """
          if item[0].startswith('_') or item[0] == "fans":
            """
            由于它是一个由sqlalchemy更改过的DO类, 会有一些sqlalchemy需要的属性, 
            但我们并不需要的属性, 剔除掉
            配合更新fans的方法, 在此不对fans变量进行处理
            """
            continue
          try:
            newValue = getattr(resDO, item[0])
            if newValue != item[1]:
              isUpdated = True
              log.info('[UPDATE] mid: %s, key: %s, new: %s, old: %s' % (i, item[0], newValue, item[1]))
              setattr(dbData, item[0], newValue)
          except BaseException as e:
            raise e
        if not isUpdated:
          log.info('[EQUAL] mid: %s' % i)
      else:
        log.info('[INSERT] mid: %s' % i)
        session.add(UserProfileDO(resData))

      session.commit()
    except BaseException as e:
      log.error('mid: %s, data: %s' % (i, res.data))
      raise e
    finally:
      log.info('[SLEEP] 2s')
      time.sleep(2)

  session.close()


def update_user_fans():
  log.info("--------update fans running--------")
  last_timestamp: int = 0
  update_delta: int = 24 * 60 * 60
  file: List[dict] = list()
  try:
    while True:
      timestamp: int = int(time.time())
      if timestamp - last_timestamp >= update_delta:
        log.info("----------update fans----------")
        session = DBSession()

        mids: Set[int] = set()
        sql: str = "select mid from bilibili"
        res: ResultProxy = session.execute(sql)
        for item in res.fetchall():
          mids.add(int(item[0]))
        log.info("mids: %s" % mids.__len__())

        for i, v in enumerate(mids):
          try:
            mid = {'mid': v}
            res: HTTPResponse = selfusepy.get('http://api.bilibili.com/x/web-interface/card', **mid)
            j: dict = json.loads(res.data)
            fans: int = int(j["data"]["follower"])
            user: UserProfileDO = session.query(UserProfileDO).filter(UserProfileDO.mid == v).first()
            if fans is None:
              raise Exception("mid: %s, fans can not be none" % v)
            log.info("i: %s, mid: %s, former fans: %s, fans: %s, delta: %s" % (i, v, user.fans, fans, fans - user.fans))
            user.fans = fans
            session.commit()
            file.append({"mid": v, "former_fans": user.fans, "fans": fans})
            time.sleep(2)
          except BaseException as e:
            log.info("mid: %s, user: %s" % (v, user))
            raise e

        session.close()
        last_timestamp = timestamp
        file_name = "%s.json" % ("%s-%s" % ("fans", timestamp))
        file_path = "data-temp/%s" % file_name
        _file.save(json.dumps(file), file_path)
        _s3.put({file_name: file_path})
        log.info("----------update fans end----------")
      else:
        time.sleep(10)
  except BaseException as e:
    log.exception(e)
    import traceback
    _email.send(email_to_addr, traceback.format_exc())


class UpdateUserFansThread(threading.Thread):
  def run(self) -> None:
    update_user_fans()

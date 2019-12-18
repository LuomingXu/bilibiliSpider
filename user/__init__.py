from typing import Set

import selfusepy
import time
from selfusepy.url import HTTPResponse

from db import DBSession, log
from user.DO import UserProfileDO
from user.Entity import UserProfile


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
          if item[0].startswith('_'):
            """
            由于它是一个由sqlalchemy更改过的DO类, 会有一些sqlalchemy需要的属性, 
            但我们并不需要的属性, 剔除掉
            """
            continue
          try:
            newValue = getattr(resDO, item[0])
            if newValue != item[1]:
              isUpdated = True
              log.info('[UPDATE] mid: %s, key: %s, new: %s, old: %s' % (i, item[0], newValue, item[1]))
              setattr(dbData, item[0], newValue)
          except Exception as e:
            log.error(e.__str__())
        if not isUpdated:
          log.info('[EQUAL] mid: %s' % i)
      else:
        log.info('[INSERT] mid: %s' % i)
        session.add(UserProfileDO(resData))

      session.commit()
    except Exception as e:
      log.exception(e)
      log.error('mid: %s, data: %s' % (i, res.data))
    finally:
      log.info('[SLEEP] 2.5s')
      time.sleep(2.5)

  session.close()

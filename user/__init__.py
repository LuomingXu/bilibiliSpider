from typing import Set, List

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
      dbData: UserProfileDO = session.query(UserProfileDO).filter_by(mid = i).first()
      if dbData:  # 存在
        resDbData: UserProfileDO = UserProfileDO(resData)
        for item in vars(dbData).items():
          if item[0].startswith('_'):
            continue
          try:
            newValue = getattr(resDbData, item[0])
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
      log.info(i.__str__())
      log.info(res.data)
    finally:
      log.info('[SLEEP] 2.5s')
      time.sleep(2.5)

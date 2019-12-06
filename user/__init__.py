from typing import Set, List

import selfusepy
import time
from selfusepy.url import HTTPResponse

from db import DBSession, log
from user.DO import UserProfileDO
from user.Entity import UserProfile


def __main__(mids: Set[int]):
  DOs: List[UserProfileDO] = []

  for i in mids:
    if isExist(i):
      continue

    mid = {'mid': i}
    res: HTTPResponse = selfusepy.get('https://api.bilibili.com/x/space/acc/info', **mid)

    try:
      resData: UserProfile = selfusepy.parse_json(res.data, UserProfile())
      DOs.append(UserProfileDO(resData))
    except Exception as e:
      log.exception(e)
      log.info(i.__str__())
      log.info(res.data)
      saveDOs(DOs)
    finally:
      log.info('user sleep 5s')
      time.sleep(5)
  saveDOs(DOs)


def isExist(mid: int):
  session = DBSession()
  obj: UserProfileDO = session.query(UserProfileDO).filter_by(mid = mid).first()
  if obj:
    return True
  return False


def saveDOs(DOs: List[UserProfileDO]):
  session = DBSession()
  try:
    session.bulk_save_objects(DOs)
    session.commit()
    log.info('count: %s. insert success.' % DOs.__len__())
  except Exception as e:
    session.rollback()
    log.exception(e)
    log.info(DOs.__len__())
  finally:
    DOs.clear()
    session.close()

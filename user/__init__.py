import selfusepy
from typing import List
from user.Entity import UserProfile
from user.DO import UserProfileDO
from db import DBSession
from selfusepy.url import HTTPResponse
from selfusepy.utils import Logger

log = Logger('./error.log').logger


def __main__(mids: List[int]):
  DOs: List[UserProfileDO] = []

  for i in mids:
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
      DOs.clear()
  saveDOs(DOs)


def saveDOs(DOs: List[UserProfileDO]):
  session = DBSession()
  try:
    session.bulk_save_objects(DOs)
    session.commit()
    log.info('count: %s. insert success.' % DOs.__len__())
  except Exception as e:
    log.exception(e)
    log.info(DOs.__len__())
  finally:
    DOs.clear()
    session.close()

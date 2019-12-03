# encoding:UTF-8
import json
import time
from typing import List

import res
from Bilibili import UserProfile
from BilibiliDO import UserProfileDO
from db import DBSession
from utils import ShowProcess, Logger

if __name__ == '__main__':
  max = 35633398
  process_bar = ShowProcess(max, 'Done')
  session = DBSession()

  http = res.Request()
  DOs: List[UserProfileDO] = []

  log = Logger('error.log').logger
  for i in range(10001, max):
    mid = {'mid': i}
    http.get('https://api.bilibili.com/x/space/acc/info', **mid)

    try:
      resData = json.loads(http.res.data, object_hook = UserProfile.from_dict)
      DOs.append(UserProfileDO(resData))
    except Exception:
      log.info(i.__str__())
      log.info(http.res.data)
      session.bulk_save_objects(DOs)
      session.commit()
      DOs.clear()

    try:
      if i % 100 == 0:
        session.bulk_save_objects(DOs)
        session.commit()
        DOs.clear()
        print('i: %s. insert success.' % i)
    except Exception:
      log.info(i.__str__())
      log.info(DOs.__len__())

    process_bar.show_process()
    time.sleep(2.25)

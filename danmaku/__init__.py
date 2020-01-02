import json
import time
from typing import List, MutableMapping

import selfusepy
from selfusepy import HTTPResponse

import _file
import config
from config import log, chromeUserAgent, red
from danmaku.DO import DanmakuDO, DanmakuRealationDO, AVCidsDO
from danmaku.Entity import AvDanmakuCid


def is_req_danmaku(cid_len: int, aid: int) -> bool:
  if cid_len <= 3:
    return False
  else:
    key = str(aid.__str__() + '-req-times')
    res = red.get(key)
    if res:
      res = int(res)
    else:
      red.set(key, 1)
      res = 1
    if (cid_len < 10 and res > 6) or (cid_len >= 10 and res > 3):
      log.info('aid: %s, req times: %s. %s' % (aid, res, True))
      return True
    else:
      red.incr(key, 1)
      log.info('aid: %s, req times: %s. %s' % (aid, res, False))
      return False


def getting_data(aids: List[int]) -> MutableMapping[str, str]:
  log.info('Total aids: %s' % aids.__len__())
  file_map: MutableMapping[str, str] = {}
  for i, aid in enumerate(aids):
    resAllCids: HTTPResponse = selfusepy.get('https://www.bilibili.com/widget/getPageList?aid=' + str(aid))
    danmakuCids: List[AvDanmakuCid] = list()
    try:
      l = json.loads(resAllCids.data)
      log.info('[Start] i: %s, aid: %s, cids length: %s' % (i, aid, l.__len__()))
      if isinstance(json.loads(resAllCids.data), list):
        for item in l:
          danmakuCids.append(selfusepy.parse_json(json.dumps(item), AvDanmakuCid()))

      if is_req_danmaku(danmakuCids.__len__(), aid):  # 如果有大量的cid, 就只进行有限获取
        log.info('[Continue] do not get cids. aid: %s' % aid)
        continue

      time.sleep(2)
      for j, cidE in enumerate(danmakuCids):
        log.info('[Request] j: %s, cid: %s' % (j, cidE.cid))
        res: HTTPResponse = selfusepy.get('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(cidE.cid),
                                          head = chromeUserAgent)

        file_name = '%s/danmaku/%s-%s-%s.xml' % (config.date, aid, cidE.cid, time.time_ns())
        file_path = 'data-temp/%s' % file_name
        file_map[file_name] = file_path
        _file.save(str(res.data, encoding = 'utf-8').replace('\\n', ''), file_path)

        time.sleep(2)

      log.info('[Done] i: %s, aid: %s' % (i, aid))
    except Exception as e:
      log.exception(e)
      log.error(resAllCids.data)
      log.error(aid)
      raise e
  return file_map

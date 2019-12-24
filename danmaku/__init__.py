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


def do_not_get_cid(aid: int) -> bool:
  key = str(aid.__str__() + '-req-times')
  res = red.get(key)
  if res is None:
    red.set(key, 1)
    return False
  else:
    log.info('aid: %s, req times: %s' % (aid, res))
    if res >= 3:
      return True
    else:
      red.incr(key, 1)
      return False


def getting_data(aids: List[int]) -> MutableMapping[str, str]:
  log.info('Total aids: %s' % aids.__len__())
  file_map: MutableMapping[str, str] = {}
  for i, aid in enumerate(aids):
    resAllCids: HTTPResponse = selfusepy.get('https://www.bilibili.com/widget/getPageList?aid=' + str(aid))
    danmakuCids: List[AvDanmakuCid] = list()
    l = json.loads(resAllCids.data)
    log.info('[Start] i: %s, aid: %s, cids length: %s' % (i, aid, l.__len__()))
    if isinstance(json.loads(resAllCids.data), list):
      for item in l:
        danmakuCids.append(selfusepy.parse_json(json.dumps(item), AvDanmakuCid()))

    if danmakuCids.__len__() > 32 and do_not_get_cid(aid):  # 如果有大量的cid, 就只获取三次
      log.info('[Continue] do not get cids. aid: %s' % aid)
      continue

    time.sleep(2)
    for j, cidE in enumerate(danmakuCids):
      log.info('[Request] i: %s, cid: %s' % (j, cidE.cid))
      res: HTTPResponse = selfusepy.get('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(cidE.cid),
                                        head = chromeUserAgent)

      file_name = '%s/danmaku/%s-%s-%s.xml' % (config.date, aid, cidE.cid, time.time_ns())
      file_path = 'data-temp/%s' % file_name
      file_map[file_name] = file_path
      _file.save(str(res.data, encoding = 'utf-8').replace('\\n', ''), file_path)

      time.sleep(2)

    log.info('[Done] i: %s, aid: %s' % (i, aid))

  return file_map

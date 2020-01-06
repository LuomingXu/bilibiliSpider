import json
import time
from typing import List, MutableMapping

import selfusepy
from selfusepy import HTTPResponse

import _file
import config
from config import log, chromeUserAgent, red
from danmaku.DO import DanmakuDO, DanmakuRealationDO, AVCidsDO
from danmaku.Entity import AvDanmakuCid, ReqTimes


def is_req_danmaku(aid: int, cid_len: int) -> (bool, int):
  if cid_len == 1:
    return True, -1
  else:
    key = '%s-req-times' % aid
    res = red.get(key)
    req: ReqTimes = ReqTimes()
    if res:  # exist
      try:
        req = selfusepy.parse_json(str(res, encoding = 'utf-8'), ReqTimes())
      except Exception:  # 兼容v0.0.5的req-times, 可于过段时间后删去
        i = int(res)
        req.cid_len = cid_len
        req.req_times = i
    else:  # not exist, init
      red.set(key, json.dumps(ReqTimes(cid_len, 1).__dict__, default = int))
      expire_policy(key, cid_len)
      return True, 1

    if is_out_of_max_req_times(cid_len, req.req_times):
      return False, req.req_times
    else:
      req.req_times += 1
      red.set(key, json.dumps(req.__dict__, default = int))
      expire_policy(key, cid_len)
      return True, req.req_times


def expire_policy(key: str, cid_len: int):
  if cid_len <= 10:
    red.expire(key, 2 * 3600 * 24)  # 2 day
    return
  if cid_len <= 26:
    red.expire(key, 5 * 3600 * 24)
    return
  if cid_len <= 100:
    red.expire(key, 10 * 3600 * 24)
    return
  red.expire(key, 18 * 3600 * 24)
  return


def is_out_of_max_req_times(cid_len: int, times: int):
  if cid_len <= 10:
    if times >= 8:
      return True
    else:
      return False
  if cid_len <= 26:
    if times >= 6:
      return True
    else:
      return False
  if cid_len <= 100:
    if times >= 2:
      return True
    else:
      return False
  if cid_len > 100:
    if times >= 1:
      return True
    else:
      return False
  log.error('Here can not be reached')


def getting_data(aids: List[int]) -> MutableMapping[str, str]:
  log.info('Total aids: %s' % aids.__len__())
  file_map: MutableMapping[str, str] = {}
  for i, aid in enumerate(aids):
    resAllCids: HTTPResponse = selfusepy.get('https://www.bilibili.com/widget/getPageList?aid=' + str(aid))

    try:
      data: str = str(resAllCids.data, encoding = 'utf-8')
      danmakuCids: List[AvDanmakuCid] = selfusepy.parse_json_array(data, AvDanmakuCid())
      log.info('[Start] i: %s, aid: %s, cids length: %s' % (i, aid, danmakuCids.__len__()))

      go_on, times = is_req_danmaku(aid, danmakuCids.__len__())
      log.info('len: %s, req times:%s. go_on: %s' % (danmakuCids.__len__(), times, go_on))
      if not go_on:  # 如果有大量的cid, 就只进行有限获取
        log.info('[Continue] do not get cids. aid: %s' % aid)
        continue

      json_file_name = '%s/danmaku/%s.json' % (config.date, aid)
      json_file_path = 'data-temp/%s' % json_file_name
      file_map[json_file_name] = json_file_path
      _file.save(data, json_file_path)

      time.sleep(2)
      for j, cidE in enumerate(danmakuCids):
        log.info('[Request] j: %s, cid: %s' % (j, cidE.cid))
        res: HTTPResponse = selfusepy.get('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(cidE.cid),
                                          head = chromeUserAgent)

        xlm_file_name = '%s/danmaku/%s-%s-%s.xml' % (config.date, aid, cidE.cid, time.time_ns())
        xlm_file_path = 'data-temp/%s' % xlm_file_name
        file_map[xlm_file_name] = xlm_file_path
        _file.save(str(res.data, encoding = 'utf-8').replace('\\n', ''), xlm_file_path)

        time.sleep(2)

      log.info('[Done] i: %s, aid: %s' % (i, aid))
    except Exception as e:
      log.exception(e)
      log.error(resAllCids.data)
      log.error(aid)
      import traceback, _email
      from config import email_to_addr
      _email.send(email_to_addr, traceback.format_exc() + '\naid: %d' % aid)
      time.sleep(10)
  return file_map

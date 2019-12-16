import asyncio
import json
import time
from datetime import timezone, timedelta, datetime
from typing import List, MutableMapping, Set

import selfusepy
from bs4 import BeautifulSoup
from bs4 import Tag
from selfusepy import HTTPResponse
from sqlalchemy.engine import ResultProxy

from danmaku.DO import DanmakuDO, DanmakuRealationDO, AVCidsDO
from danmaku.Entity import AvDanmakuCid
from db import DBSession, engine, log
from online.DO import AVInfoDO

i_for_queryAllCidOfAv = 0
i_for_queryAllDanmakuOfCid = 0
START_TIME_for_queryAllCidOfAv = 0
START_TIME_for_queryAllDanmakuOfCid = 0
REQUEST_TIME_DELTA = 2500
NEED_FETCH_CIDs: Set[int] = set()
NEED_SAVE_DANMAKUs: MutableMapping[int, List[Tag]] = {}
CID_MaxLimit: MutableMapping[int, int] = {}
chromeUserAgent: dict = {
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}


async def query_all_cid_of_av(avInfo: AVInfoDO):
  global i_for_queryAllCidOfAv
  log.info('[START] i: %s' % i_for_queryAllCidOfAv)

  delta = (START_TIME_for_queryAllCidOfAv + i_for_queryAllCidOfAv * REQUEST_TIME_DELTA - int(
    round(time.time() * 1000))) / 1000
  time.sleep(delta if delta > 0 else 0)
  i_for_queryAllCidOfAv += 1

  log.info('[REQUEST] av\'s cids, aid: %s' % avInfo.aid)
  res: HTTPResponse = await selfusepy.get_async(
    'https://www.bilibili.com/widget/getPageList?aid=' + str(avInfo.aid))
  map: MutableMapping[int, AvDanmakuCid] = {}
  try:
    j = json.loads(res.data)
    if isinstance(json.loads(res.data), list):
      for item in j:
        map[item['cid']] = selfusepy.parse_json(json.dumps(item), AvDanmakuCid())
    log.info('[REQUEST] Done')
    log.info('[DATA] aid: %s, cid len: %s' % (avInfo.aid, map.__len__()))
    await query_danmaku_by_cid(avInfo.aid, map)
  except Exception as e:
    log.exception(e)
    log.error('aid: %s' % avInfo.aid)


async def query_danmaku_by_cid(aid: int, danmakuCidsMap: MutableMapping[int, AvDanmakuCid]):
  sql: str = 'select cid from av_cids where cid in (%s)' % ','.join('%s' % item for item in danmakuCidsMap.keys())
  res: ResultProxy = await execute_sql(sql)
  for item in res.fetchall():
    danmakuCidsMap.pop(item[0])
  log.info('[DATA] aid: %s, cid not exist len: %s' % (aid, danmakuCidsMap.__len__()))
  NEED_FETCH_CIDs.update(danmakuCidsMap.keys())


async def query_all_danmaku_of_cid(cid: int):
  global i_for_queryAllDanmakuOfCid
  log.info('[START] i: %s' % i_for_queryAllDanmakuOfCid)

  delta = (START_TIME_for_queryAllDanmakuOfCid + i_for_queryAllDanmakuOfCid * REQUEST_TIME_DELTA - int(
    round(time.time() * 1000))) / 1000
  time.sleep(delta if delta > 0 else 0)
  i_for_queryAllDanmakuOfCid += 1

  res: HTTPResponse = await selfusepy.get_async('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(cid),
                                                head = chromeUserAgent)

  soup: BeautifulSoup = BeautifulSoup(markup = str(res.data, encoding = 'utf-8').replace('\\n', ''),
                                      features = 'lxml')
  try:
    NEED_SAVE_DANMAKUs[cid] = soup.find_all(name = 'd')
    CID_MaxLimit[cid] = int(soup.find(name = 'maxlimit').text)
  except Exception as e:
    log.exception(e)
    log.error('cid: %s' % cid)


async def execute_sql(sql: str) -> ResultProxy:
  conn = engine.connect()
  try:
    return conn.execute(sql)
  except Exception as e:
    log.exception(e)
  finally:
    conn.close()


def main():
  log.info('[Danmaku Task]')
  session = DBSession()

  # todo 改为一个sql, 在sql里面删去已经存在的不需要进行获取的av info
  avInfos: List[AVInfoDO] = session.query(AVInfoDO).order_by(AVInfoDO.create_time.desc())

  loop = asyncio.get_event_loop()

  # 获取所有需要进行添加的cid
  START_TIME_for_queryAllCidOfAv = int(round(time.time() * 1000))
  tasks = list()
  for i, item in enumerate(avInfos):
    if i == 2:
      break
    tasks.append(query_all_cid_of_av(item))
  loop.run_until_complete(asyncio.wait(tasks))
  print(NEED_FETCH_CIDs.__len__())

  # 获取cid对应的弹幕列表
  START_TIME_for_queryAllDanmakuOfCid = int(round(time.time() * 1000))
  tasks = list()
  if NEED_FETCH_CIDs.__len__() > 1:
    for item in NEED_FETCH_CIDs:
      tasks.append(query_all_danmaku_of_cid(item))
    loop.run_until_complete(asyncio.wait(tasks))

  print(NEED_SAVE_DANMAKUs.__len__())
  loop.close()
  log.info('[Danmaku Task Done]')

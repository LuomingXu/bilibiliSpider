import asyncio
import json
import multiprocessing
import time
from datetime import timezone, timedelta, datetime
from multiprocessing import Pool
from typing import List, MutableMapping, Set

import selfusepy
from bs4 import BeautifulSoup
from bs4 import Tag
from selfusepy import HTTPResponse
from sqlalchemy.engine import ResultProxy

from config import DBSession, engine, log, chromeUserAgent
from danmaku.DO import DanmakuDO, DanmakuRealationDO, AVCidsDO
from danmaku.Entity import AvDanmakuCid, CustomTag
from online.DO import AVInfoDO

Last_Request_Time = 0
i_for_queryAllCidOfAv = 0
i_for_queryAllDanmakuOfCid = 0
REQUEST_TIME_DELTA = 2500_000_000  # 请求间隔设为2.5s, 此处单位为ns
NEED_FETCH_CIDs: Set[int] = set()
NEED_SAVE_DANMAKUs: MutableMapping[int, List[Tag]] = {}
CID_MaxLimit: MutableMapping[int, int] = {}


async def query_all_cid_of_av(avInfo: AVInfoDO):
  global i_for_queryAllCidOfAv, Last_Request_Time
  log.info('[START] i: %s' % i_for_queryAllCidOfAv)

  delta = (Last_Request_Time + REQUEST_TIME_DELTA - time.time_ns()) / 1000_000_000
  time.sleep(delta if delta > 0 else 0)
  i_for_queryAllCidOfAv += 1

  log.info('[REQUEST] av\'s cids, aid: %s' % avInfo.aid)

  Last_Request_Time = time.time_ns()
  res: HTTPResponse = await selfusepy.get_async(
    'https://www.bilibili.com/widget/getPageList?aid=' + str(avInfo.aid))
  map: MutableMapping[int, AvDanmakuCid] = {}
  session = DBSession()
  try:
    j = json.loads(res.data)
    if isinstance(json.loads(res.data), list):
      for item in j:
        map[item['cid']] = selfusepy.parse_json(json.dumps(item), AvDanmakuCid())
    log.info('[REQUEST] Done')
    log.info('[DATA] aid: %s, cid len: %s' % (avInfo.aid, map.__len__()))

    # 删除已经保存aid-cid的对应关系
    sql: str = 'select cid from av_cids where aid = %s and cid in (%s)' % (
      avInfo.aid, ','.join('%s' % item for item in map.keys()))
    r: ResultProxy = await execute_sql(sql)
    exist: Set[int] = set()
    for item in r.fetchall():
      exist.add(item[0])

    for item in map.items():
      if not exist.__contains__(item[0]):
        session.add(AVCidsDO(avInfo.aid, item[1]))
    session.commit()
    await filter_cid_which_isexist(avInfo.aid, map)
  except Exception as e:
    log.error('aid: %s' % avInfo.aid)
    raise e
  finally:
    session.close()


async def filter_cid_which_isexist(aid: int, danmakuCidsMap: MutableMapping[int, AvDanmakuCid]):
  cids: str = ','.join('%s' % item for item in danmakuCidsMap.keys())
  sql: str = 'select cid from av_cids where cid in (%s) and fetch_times >= 4' % cids
  res: ResultProxy = await execute_sql(sql)
  for item in res.fetchall():
    danmakuCidsMap.pop(item[0], None)
  log.info('[DATA] aid: %s, cid fetch_times <4 len: %s' % (aid, danmakuCidsMap.__len__()))
  sql: str = 'update av_cids set fetch_times = fetch_times + 1 where cid in (%s)' % cids
  res = await execute_sql(sql)
  NEED_FETCH_CIDs.update(danmakuCidsMap.keys())


async def query_all_danmaku_of_cid(cid: int):
  global i_for_queryAllDanmakuOfCid, Last_Request_Time
  log.info('[START] i: %s' % i_for_queryAllDanmakuOfCid)

  delta = (Last_Request_Time + REQUEST_TIME_DELTA - time.time_ns()) / 1000_000_000
  time.sleep(delta if delta > 0 else 0)
  i_for_queryAllDanmakuOfCid += 1

  Last_Request_Time = time.time_ns()
  res: HTTPResponse = await selfusepy.get_async('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(cid),
                                                head = chromeUserAgent)

  soup: BeautifulSoup = BeautifulSoup(markup = str(res.data, encoding = 'utf-8').replace('\\n', ''),
                                      features = 'lxml')
  try:

    CID_MaxLimit[cid] = int(soup.find(name = 'maxlimit').text)

    # 不再保存已经达到最大数量限制的弹幕, todo, 虽然有可能后续有新的弹幕, 老的已经被清了
    sql: str = 'select count(danmaku_id) from cid_danmaku where cid = %s' % cid
    r: ResultProxy = await execute_sql(sql)
    count: int = int(r.fetchone()[0])
    log.info('cid: %s, danmaku count: %s, max limit: %s' % (cid, count, CID_MaxLimit[cid]))
    if count >= CID_MaxLimit[cid]:
      log.info('cid: %s not operate DB' % cid)
      CID_MaxLimit.pop(cid)
      return

    NEED_SAVE_DANMAKUs[cid] = soup.find_all(name = 'd')
  except Exception as e:
    log.error('cid: %s' % cid)
    raise e


def lookahead(iterable):
  """Pass through all values from the given iterable, augmented by the
  information if there are more values to come after the current one
  (True), or if it is the last value (False).
  """
  # Get an iterator and pull the first value.
  it = iter(iterable)
  last = next(it)
  # Run the iterator to exhaustion (starting from the second value).
  for val in it:
    # Report the *previous* value (more to come).
    yield last, True
    last = val
  # Report the last value.
  yield last, False


def destruct_danmaku(cid: int, danmakus: List[CustomTag]):
  danmakuMap: MutableMapping[int, DanmakuDO] = {}
  relationMap: MutableMapping[int, DanmakuRealationDO] = {}
  print('[FORMER] cid: %s, danmakus: %s' % (cid, danmakus.__len__()))
  for danmaku in danmakus:
    # 弹幕出现时间,模式,字体大小,颜色,发送时间戳,弹幕池,用户Hash,数据库ID
    obj: DanmakuDO = DanmakuDO()
    obj.content = danmaku.content
    l: list = danmaku.tag_content.split(',')
    obj.danmaku_epoch = float(l[0])
    obj.mode = int(l[1])
    obj.font_size = int(l[2])
    obj.font_color = int(l[3])
    obj.send_time = datetime.fromtimestamp(int(l[4]), timezone(timedelta(hours = 8)))
    obj.danmaku_pool = int(l[5])
    obj.user_hash = int(l[6], 16)
    # 暂不直接从数据库获取crc32数据, 太慢了
    # value = crc32.get_value(l[6])
    # if value[0] > 0:
    #   obj.user_id = value[1]
    obj.id = int(l[7])

    relation: DanmakuRealationDO = DanmakuRealationDO()
    relation.cid = cid
    relation.danmaku_id = obj.id

    danmakuMap[obj.id] = obj
    relationMap[relation.danmaku_id] = relation

  session = DBSession()
  try:
    removeExist(cid, danmakuMap, relationMap)

    if danmakuMap.__len__() == relationMap.__len__() and relationMap.__len__() == 0:
      print('cid: %s, has saved all danmaku' % cid)
      return

    session.bulk_save_objects(danmakuMap.values() if danmakuMap.values().__len__() > 0 else None)
    session.bulk_save_objects(relationMap.values() if relationMap.values().__len__() > 0 else None)
    session.commit()
  except Exception as e:
    session.rollback()
    print(e)
    print('cid: %s, has error. ' % cid)
  else:
    print('cid: %s, Saved into DB.' % cid)
  finally:
    session.close()
    print('[SAVED] danmakuMap.len: %s' % danmakuMap.__len__())
    print('[SAVED] relationMap.len: %s' % relationMap.__len__())
    danmakuMap.clear()
    relationMap.clear()


def removeExist(cid: int, danmakuMap: MutableMapping[int, DanmakuDO],
                relationMap: MutableMapping[int, DanmakuRealationDO]):
  if danmakuMap.__len__() != relationMap.__len__():
    raise BaseException('length is not match')

  conn = engine.connect()

  sql: str = 'select danmaku_id from cid_danmaku where danmaku_id in (%s) and cid = %s' % (
    ', '.join('%s' % item for item in relationMap.keys()), cid)

  ids: ResultProxy = conn.execute(sql)
  for item in ids.fetchall():
    relationMap.pop(item[0], None)

  sql = 'select id from danmaku where id in (%s)' % (
    ', '.join('%s' % str(item) for item in danmakuMap.keys()))

  ids = conn.execute(sql)
  for item in ids.fetchall():
    danmakuMap.pop(item[0], None)

  conn.close()


async def execute_sql(sql: str) -> ResultProxy:
  conn = engine.connect()
  try:
    return conn.execute(sql)
  except Exception as e:
    raise e
  finally:
    conn.close()


def main(aidList: List[int]):
  log.info('[Danmaku Task]')

  loop = asyncio.get_event_loop()

  # 获取所有需要进行添加的cid
  tasks = list()
  for item in aidList:
    temp: AVInfoDO = AVInfoDO(None)
    temp.aid = item
    tasks.append(query_all_cid_of_av(temp))
  loop.run_until_complete(asyncio.wait(tasks))
  print('Need fetch cids', NEED_FETCH_CIDs.__len__())

  # 获取cid对应的弹幕列表
  global Last_Request_Time
  Last_Request_Time = 0  # 下一队列的协程任务开始前, 将此时间清零
  tasks = list()
  if NEED_FETCH_CIDs.__len__() > 1:
    for item in NEED_FETCH_CIDs:
      tasks.append(query_all_danmaku_of_cid(item))
    loop.run_until_complete(asyncio.wait(tasks))

  print('Need save danmakus', NEED_SAVE_DANMAKUs.__len__())
  loop.close()

  pool = Pool(processes = int(multiprocessing.cpu_count() / 2))  # 使用总核心数的一半
  for item in NEED_SAVE_DANMAKUs.items():
    l: List[CustomTag] = list()  # 这边比较迷, bs4的Tag在多进程的时候, 没有办法进行传参, 所以对Tag进行了自定义封装
    for s in item[1]:
      l.append(CustomTag(s.text, s['p']))
    pool.apply_async(func = destruct_danmaku, args = (item[0], l))
  pool.close()  # 关闭进程池，表示不能在往进程池中添加进程
  pool.join()  # 等待进程池中的所有进程执行完毕，必须在close()之后调用

  log.info('[Danmaku Task Done]')

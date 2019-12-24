import asyncio
import gc
import math
import multiprocessing
from datetime import datetime
from datetime import timezone, timedelta
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from typing import List, MutableMapping, Set, AbstractSet

from bs4 import BeautifulSoup
from sqlalchemy.engine.result import ResultProxy

import online
from config import DBSession, engine, log, red
from danmaku.DO import DanmakuDO, DanmakuRealationDO, AVCidsDO
from danmaku.Entity import CustomTag
from local_processing.Entity import CustomFile, FileType


def remove_data(_map: MutableMapping[str, CustomFile]):
  """
  剔除已经存了大于3000条弹幕的cid
  """
  conn = engine.connect()
  cid_key: MutableMapping[int, str] = {}

  for file_name, file in _map.items():
    if file.file_type is FileType.Danmaku:
      l: List = file_name.split('-')
      cid_key[int(l[1])] = file_name

  sql: str = 'select danmaku_count, cid from av_cids where cid in (\'\',%s)' % ','.join(
    '%s' % item for item in cid_key.keys())
  res: ResultProxy = conn.execute(sql)
  conn.close()
  cid_count: MutableMapping[int, int] = {}
  for item in res.fetchall():
    cid_count[int(item[1])] = int(item[0])

  for cid, count in cid_count.items():
    if count >= 3000:
      _map.pop(cid_key[cid], None)


def analyze_danmaku(_map: MutableMapping[str, CustomFile]) -> (List[CustomTag], MutableMapping[int, int]):
  danmakuList: List[CustomTag] = []
  cid_aid: MutableMapping[int, int] = {}
  for file_name, file in _map.items():
    if file.file_type is FileType.Online:
      online.processing_data(file.content,
                             datetime.fromtimestamp(int(file_name) / 1_000_000_000, timezone(timedelta(hours = 8))))
    else:
      soup: BeautifulSoup = BeautifulSoup(markup = file.content, features = 'lxml')
      l: List = file_name.split('-')
      aid: int = int(l[0])
      cid: int = int(l[1])
      cid_aid[cid] = aid
      for item in soup.find_all(name = 'd'):
        danmakuList.append(CustomTag(content = item.text, tag_content = item['p'], aid = aid, cid = cid))

  print('danmakuList len: %s, cid_aid len: %s' % (danmakuList.__len__(), cid_aid.__len__()))
  return danmakuList, cid_aid


async def save_cid_aid_relation(cid_aid: MutableMapping[int, int]):
  """
  保存av与cid的关系
  """
  objs: List[AVCidsDO] = []
  session = DBSession()

  sql: str = 'select cid from av_cids where cid in (\'\', %s)' % ','.join('%s' % item for item in cid_aid.keys())

  cids: ResultProxy = await execute_sql(sql)
  exist_cids: Set[int] = set()
  for item in cids.fetchall():
    """
    保存已经存在的关系
    """
    exist_cids.add(int(item[0]))

  print('av-cid', exist_cids)
  if not exist_cids.__len__() == cid_aid.__len__():
    for cid, aid in cid_aid.items():
      if exist_cids.__contains__(cid):
        continue
      obj: AVCidsDO = AVCidsDO()
      obj.cid = cid
      obj.aid = aid
      objs.append(obj)
      print('obj', obj)

    try:
      session.bulk_save_objects(objs)
      session.commit()
    except Exception as e:
      session.rollback()
      raise e
    else:
      log.info('[Saved] av-cid relation. len: %s' % objs.__len__())
      print(objs.__str__())
    finally:
      session.close()
  else:
    log.info('All av-cid relation exist')


def save_danmaku_to_db(danmakuList: List[CustomTag], cid_aid: MutableMapping[int, int]):
  print('[FORMER] danmakuList len: %s, cid_aid len: %s' % (danmakuList.__len__(), cid_aid.__len__()))
  cids: AbstractSet[int] = cid_aid.keys()
  danmakuMap: MutableMapping[int, DanmakuDO] = {}
  relationMap: MutableMapping[int, DanmakuRealationDO] = {}
  cid_danmakuIdSet: MutableMapping[int, Set[int]] = {}
  for danmaku in danmakuList:
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
    obj.id = int(l[7])

    relation: DanmakuRealationDO = DanmakuRealationDO()
    relation.cid = danmaku.cid
    relation.danmaku_id = obj.id

    danmakuMap[obj.id] = obj
    relationMap[obj.id] = relation

    if cid_danmakuIdSet.get(danmaku.cid) is None:
      cid_danmakuIdSet[danmaku.cid] = set()
      cid_danmakuIdSet[danmaku.cid].add(obj.id)
    else:
      cid_danmakuIdSet[danmaku.cid].add(obj.id)

  print('[Done] danmakus split')
  del danmakuList
  gc.collect()

  session = DBSession()
  try:
    removeExist(danmakuMap, relationMap, cids)

    if danmakuMap.__len__() == relationMap.__len__() and relationMap.__len__() == 0:
      return

    print(
      'Removed exist ids, danmaku map len: %s, relation map len: %s' % (danmakuMap.__len__(), relationMap.__len__()))

    session.bulk_save_objects(danmakuMap.values() if danmakuMap.values().__len__() > 0 else None)
    session.bulk_save_objects(relationMap.values() if relationMap.values().__len__() > 0 else None)
    session.commit()
  except Exception as e:
    session.rollback()
    print(e)
    raise e
  else:
    print('Save to DB success')
    for cid, value in cid_danmakuIdSet.items():
      red.sadd(cid, *value)
      print('[Saved] redis. cid: %s, len: %s' % (cid, value.__len__()))
  finally:
    session.close()
    print('[SAVED] danmakuMap.len: %s' % danmakuMap.__len__())
    print('[SAVED] relationMap.len: %s' % relationMap.__len__())
    del danmakuMap
    del relationMap
    gc.collect()


def removeExist(danmakuMap: MutableMapping[int, DanmakuDO],
                relationMap: MutableMapping[int, DanmakuRealationDO], cids: AbstractSet[int]):
  """
  剔除已经存在的danmaku
  """
  print('from redis get cids: %s' % cids.__len__())
  cids_all_danmakuId: Set[int] = set()
  for cid in cids:
    for item in red.smembers(cid):
      cids_all_danmakuId.add(int(item))

  print('all danmaku len: %s' % cids_all_danmakuId.__len__())
  for _id in cids_all_danmakuId:
    danmakuMap.pop(_id, None)
    relationMap.pop(_id, None)


async def execute_sql(sql: str) -> ResultProxy:
  conn = engine.connect()
  try:
    return conn.execute(sql)
  except Exception as e:
    raise e
  finally:
    conn.close()


def main(_map: MutableMapping[str, CustomFile]):
  """
  将map分成几组进行多进程处理
  """
  log.info('multiprocess tasks')
  cpu_use_number = int(multiprocessing.cpu_count() / 3 * 2)  # 使用总核心数的2/3
  pool = Pool(processes = cpu_use_number)
  size = int(math.ceil(_map.__len__() / float(cpu_use_number)))
  map_temp: MutableMapping[str, CustomFile] = {}

  res: List[ApplyResult] = list()
  for i, item in enumerate(_map.items()):
    map_temp[item[0]] = item[1]
    if map_temp.__len__() % size == 0:
      res.append(pool.apply_async(func = analyze_danmaku, args = (map_temp,)))
      map_temp = {}
  res.append(pool.apply_async(func = analyze_danmaku, args = (map_temp,)))
  pool.close()
  pool.join()
  log.info('[Done] analyze')
  del _map
  gc.collect()

  try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
      asyncio.set_event_loop(asyncio.new_event_loop())
      loop = asyncio.get_event_loop()

    tasks: list = list()
    for item in res:
      value = item.get()
      tasks.append(save_cid_aid_relation(value[1]))
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    log.info('[Done] av-cid relation')

    pool = Pool(processes = cpu_use_number)
    for item in res:
      value = item.get()
      pool.apply_async(func = save_danmaku_to_db, args = (value[0], value[1],))
    pool.close()
    pool.join()
    log.info('[Done] danmaku')
    log.info('[DONE] analyze spiders\' data')
  except Exception as e:
    raise e

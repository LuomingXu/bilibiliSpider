import asyncio
import gc
import math
import multiprocessing
from datetime import datetime
from datetime import timezone, timedelta
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from typing import List, MutableMapping, Set

from bs4 import BeautifulSoup
from sqlalchemy.engine.result import ResultProxy

import online
from config import DBSession, engine, log
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
      _map.pop(cid_key[cid])


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
  return danmakuList, cid_aid


async def save_cid_aid_relation(cid_aid: MutableMapping[int, int]):
  """
  保存av与cid的关系
  """
  objs: List[AVCidsDO] = []
  session = DBSession()

  sql: str = 'select cid from av_cids where cid in (\'\', %s)' % ','.join('%s' % item for item in cid_aid.keys())

  cids: ResultProxy = await execute_sql(sql)
  for item in cids.fetchall():
    """
    剔除已经存在的关系
    """
    cid_aid.pop(item[0])

  if cid_aid.__len__() > 0:
    for cid, aid in cid_aid.items():
      obj: AVCidsDO = AVCidsDO()
      obj.cid = cid
      obj.aid = aid
      objs.append(obj)

      try:
        session.bulk_save_objects(objs)
      except Exception as e:
        session.rollback()
        raise e
      else:
        log.info('[Saved] av-cid relation')
      finally:
        session.close()


def save_danmaku_to_db(danmakuList: List[CustomTag]):
  danmakuMap: MutableMapping[int, DanmakuDO] = {}
  relationMap: MutableMapping[int, DanmakuRealationDO] = {}
  print('[FORMER] danmakus: %s' % (danmakuList.__len__()))
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

  print('[Done] danmakus split')
  del danmakuList
  gc.collect()

  session = DBSession()
  try:

    loop = asyncio.get_event_loop()
    if loop.is_closed():
      asyncio.set_event_loop(asyncio.new_event_loop())
      loop = asyncio.get_event_loop()
    loop.run_until_complete(removeExist(danmakuMap, relationMap))
    loop.close()

    if danmakuMap.__len__() == relationMap.__len__() and relationMap.__len__() == 0:
      return

    cid_count: MutableMapping[int, int] = {}
    for relation in relationMap.values():
      cid = relation.cid
      if cid_count.get(cid) is None:
        cid_count[cid] = 1
      else:
        cid_count[cid] += 1

    sql: str = ''.join(
      'update av_cids set danmaku_count = %s where cid = %s;' % item for item in cid_count)
    print('update sql: %s' % sql)
    session.execute(sql)

    session.bulk_save_objects(danmakuMap.values() if danmakuMap.values().__len__() > 0 else None)
    session.bulk_save_objects(relationMap.values() if relationMap.values().__len__() > 0 else None)
    session.commit()
  except Exception as e:
    session.rollback()
    raise e
  else:
    print('Saved success')
  finally:
    session.close()
    print('[SAVED] danmakuMap.len: %s' % danmakuMap.__len__())
    print('[SAVED] relationMap.len: %s' % relationMap.__len__())
    del danmakuMap
    del relationMap
    gc.collect()


async def removeExist(danmakuMap: MutableMapping[int, DanmakuDO],
                      relationMap: MutableMapping[int, DanmakuRealationDO]):
  """
  剔除已经存在的danmaku
  """
  ids: List[int] = list()
  for _id in danmakuMap.keys():
    ids.append(_id)

  size = 1_000

  ids_spliced = [ids[i:i + size] for i in range(0, len(ids), size)]
  for item in ids_spliced:
    sql: str = 'select id from danmaku where id in (\'\', %s)' % (
      ', '.join('%s' % _id for _id in item))

    exist_ids: ResultProxy = await execute_sql(sql)
    resData = exist_ids.fetchall()
    print('exist danmaku ids len: %s' % resData.__len__())
    for column in resData:
      danmakuMap.pop(column[0])
      relationMap.pop(column[0])

  print('Removed exist ids, danmaku map len: %s, relation map len: %s' % (danmakuMap.__len__(), relationMap.__len__()))


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
  log.info('removing data')  # 剔除弹幕过多的cid
  remove_data(_map)
  log.info('Current map len: %s' % _map.__len__())

  log.info('multiprocess tasks')
  cpu_use_number = int(multiprocessing.cpu_count() / 3 * 2)  # 使用总核心数的2/3
  pool = Pool(processes = cpu_use_number)
  size = int(math.ceil(_map.__len__() / float(cpu_use_number)))
  map_temp: MutableMapping[str, CustomFile] = {}

  res: Set[ApplyResult] = set()
  for i, item in enumerate(_map.items()):
    map_temp[item[0]] = item[1]
    if map_temp.__len__() % size == 0:
      res.add(pool.apply_async(func = analyze_danmaku, args = (map_temp,)))
      map_temp = {}
  res.add(pool.apply_async(func = analyze_danmaku, args = (map_temp,)))
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
      pool.apply_async(func = save_danmaku_to_db, args = (value[0],))
    pool.close()
    pool.join()
    log.info('[Done] danmaku')
    log.info('[DONE] analyze spiders\' data')
  except Exception as e:
    raise e
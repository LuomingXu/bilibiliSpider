import asyncio
import gc
import math
import multiprocessing
import traceback
from collections import Counter
from datetime import datetime
from datetime import timezone, timedelta
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from queue import Queue
from typing import List, MutableMapping, Set, AbstractSet

import selfusepy
from bs4 import BeautifulSoup
from sqlalchemy.engine.result import ResultProxy

import online
from config import DBSession, engine, log, red, cpu_use_number
from danmaku.DO import DanmakuDO, DanmakuRealationDO, AVCidsDO
from danmaku.Entity import CustomTag, AvDanmakuCid
from local_processing.Entity import CustomFile, FileType


def analyze_danmaku(q: Queue, _map: MutableMapping[str, CustomFile]) -> \
    (List[CustomTag], MutableMapping[int, int], MutableMapping[int, AvDanmakuCid]):
  danmakuList: List[CustomTag] = []
  cid_aid: MutableMapping[int, int] = {}
  cid_info: MutableMapping[int, AvDanmakuCid] = {}
  print(multiprocessing.current_process().name, 'analyze danmakus')
  try:
    for file_name, file in _map.items():
      if file.file_type is FileType.Online:
        online.processing_data(file.content, file.create_time)
      elif file.file_type is FileType.AvCids:
        l: List[AvDanmakuCid] = selfusepy.parse_json_array(file.content, AvDanmakuCid())
        for item in l:
          cid_info[item.cid] = item
      elif file.file_type is FileType.Danmaku:
        soup: BeautifulSoup = BeautifulSoup(markup = file.content, features = 'lxml')
        cid_aid[file.cid] = file.aid
        for item in soup.find_all(name = 'd'):
          danmakuList.append(CustomTag(content = item.text, tag_content = item['p'], aid = file.aid, cid = file.cid))
  except BaseException:  # save exception to queue waiting for main thread process
    name = multiprocessing.current_process().name
    _map: MutableMapping[str, str] = {name: traceback.format_exc()}
    q.put(_map)
    print('Oops: ', name)
  else:
    print('danmakuList len: %s, cid_aid len: %s' % (danmakuList.__len__(), cid_aid.__len__()))

  return danmakuList, cid_aid, cid_info


async def save_cid_aid_relation(cid_aid: MutableMapping[int, int], cid_info: MutableMapping[int, AvDanmakuCid]):
  """
  保存av与cid的关系
  """
  if cid_aid.keys().__len__() < 1:
    return
  objs: List[AVCidsDO] = []

  sql: str = 'select cid from av_cids where cid in (%s)' % ','.join('%s' % item for item in cid_aid.keys())

  cids: ResultProxy = await execute_sql(sql)
  exist_cids: Set[int] = set()
  for item in cids.fetchall():
    """
    保存已经存在的关系
    """
    exist_cids.add(int(item[0]))

  print('exist cids: ', exist_cids)
  if not exist_cids.__len__() == cid_aid.__len__():
    session = DBSession()
    for cid, aid in cid_aid.items():
      if exist_cids.__contains__(cid):
        continue
      obj: AVCidsDO = AVCidsDO()
      obj.cid = cid
      obj.aid = aid
      objs.append(obj)
    for cid in exist_cids:
      cid_info.pop(cid, None)

    try:
      if cid_info.values().__len__() > 0:
        sql_update: str = ''.join(
          'update av_cids set page = %s, page_name = %s where cid = %s;' % (item.page, item.pagename, item.cid)
          for item in cid_info.values())
        await execute_sql(sql_update)
      session.bulk_save_objects(objs)
      session.commit()
    except BaseException as e:
      session.rollback()
      raise e
    else:
      log.info('[Saved] av-cid relation. len: %s' % objs.__len__())
      print(objs.__str__())
    finally:
      session.close()
  else:
    log.info('All av-cid relation exist')


def deconstruct_danmaku(danmakuList: List[CustomTag], cid_aid: MutableMapping[int, int]) -> (
    MutableMapping[int, DanmakuDO], MutableMapping[int, DanmakuRealationDO], MutableMapping[int, Set[int]]):
  print('[Start] danmaku deconstruct len: %s, cid_aid len: %s' % (danmakuList.__len__(), cid_aid.__len__()))
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

  print('[Done] danmaku deconstruct')
  del danmakuList
  gc.collect()
  return danmakuMap, relationMap, cid_danmakuIdSet


def save_danmaku_to_db(q: Queue, danmakuMap: MutableMapping[int, DanmakuDO],
                       relationMap: MutableMapping[int, DanmakuRealationDO],
                       cid_danmakuIdSet: MutableMapping[int, Set[int]]):
  session = DBSession()
  try:
    print(
      '[After Removed Program ids] danmaku len: %s, relation len: %s' % (danmakuMap.__len__(), relationMap.__len__()))
    remove_db_exist_ids(danmakuMap, relationMap, cid_danmakuIdSet.keys())
    print('[After Removed DB ids] danmaku len: %s, relation len: %s' % (danmakuMap.__len__(), relationMap.__len__()))

    if danmakuMap.__len__() != relationMap.__len__():
      raise Exception("danmaku's len is not eq relation's len")

    if danmakuMap.values():
      session.bulk_save_objects(danmakuMap.values())
    if relationMap.values():
      session.bulk_save_objects(relationMap.values())
    session.commit()
  except BaseException:
    session.rollback()
    name = multiprocessing.current_process().name
    _map: MutableMapping[str, str] = {name: traceback.format_exc()}
    q.put(_map)
    print('Oops: ', name)
  else:
    print('Save to DB success, len: %s' % danmakuMap.__len__())
    for cid, value in cid_danmakuIdSet.items():
      try:
        red.sadd(cid, *value)
      except BaseException:
        traceback.print_exc()
        print('[ERROR] redis. cid: %s' % cid)
    print('[DONE] save danmaku ids to redis')
  finally:
    session.close()
    del danmakuMap
    del relationMap
    gc.collect()


def remove_program_exist_ids(danmakuMap: MutableMapping[int, DanmakuDO],
                             relationMap: MutableMapping[int, DanmakuRealationDO],
                             cid_danmakuIdSet: MutableMapping[int, Set[int]]):
  res: List = list()
  for cid in cid_danmakuIdSet.keys():
    res.extend(red.lrange('program-temp-%s' % cid, 0, -1))

  count: dict = dict(Counter(res))
  duplicate_ids: Set[int] = set()
  for key, value in count.items():
    if value > 1:
      duplicate_ids.add(key)

  duplicate_danmaku: MutableMapping[int, DanmakuDO] = {}
  duplicate_relation: MutableMapping[int, DanmakuRealationDO] = {}
  for id in duplicate_ids:
    danmaku = danmakuMap.pop(id, None)
    relation = relationMap.pop(id, None)
    if danmaku is not None:
      duplicate_danmaku[id] = danmaku
    if relation is not None:
      duplicate_relation[id] = relation

  if duplicate_danmaku.__len__() > 0:
    f = open('./%s-danmaku.txt' % multiprocessing.current_process().name, 'w', encoding = 'utf-8')
    f.write('\n'.join('%s->%s' % item for item in duplicate_danmaku.items()))
  if duplicate_relation.__len__() > 0:
    f = open('./%s-relation.txt' % multiprocessing.current_process().name, 'w', encoding = 'utf-8')
    f.write('\n'.join('%s->%s' % item for item in duplicate_relation.items()))


def remove_db_exist_ids(danmakuMap: MutableMapping[int, DanmakuDO],
                        relationMap: MutableMapping[int, DanmakuRealationDO], cids: AbstractSet[int]):
  """
  剔除数据库中已经存在的danmaku
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
  except BaseException as e:
    raise e
  finally:
    conn.close()


def main(_map: MutableMapping[str, CustomFile]):
  """
  将map分成几组进行多进程处理
  """
  q = multiprocessing.Manager().Queue()
  log.info('multiprocess tasks')
  pool = Pool(processes = cpu_use_number)
  size = int(math.ceil(_map.__len__() / float(cpu_use_number)))
  map_temp: MutableMapping[str, CustomFile] = {}

  res: List[ApplyResult] = list()
  for key, value in _map.items():
    map_temp[key] = value
    if map_temp.__len__() % size == 0:
      res.append(pool.apply_async(func = analyze_danmaku, args = (q, map_temp,)))
      map_temp = {}
  res.append(pool.apply_async(func = analyze_danmaku, args = (q, map_temp,)))
  pool.close()
  pool.join()
  if q.qsize() > 0:  # 当queue的size大于0的话, 那就是进程里面出现了错误, raise, 结束任务
    log.error('analyze occurs error')
    raise Exception(q)
  log.info('[Done] analyze')
  del _map
  gc.collect()

  try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
      asyncio.set_event_loop(asyncio.new_event_loop())
      loop = asyncio.get_event_loop()

    log.info('[Start] aid-cid relation')
    tasks: list = list()
    for item in res:
      value = item.get()
      tasks.append(save_cid_aid_relation(value[1], value[2]))
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    log.info('[Done] av-cid relation')

    log.info('[Start] danmaku deconstruct')
    danmaku_data_res: List[ApplyResult] = list()
    pool2 = Pool(processes = cpu_use_number)
    for item in res:
      value = item.get()
      danmaku_data_res.append(pool2.apply_async(func = deconstruct_danmaku, args = (value[0], value[1],)))
    pool2.close()
    pool2.join()
    log.info('[Done] deconstruct')

    log.info('[Start] save danmaku to db')
    pool3 = Pool(processes = cpu_use_number)
    for item in danmaku_data_res:
      value = item.get()
      pool3.apply_async(func = save_danmaku_to_db, args = (q, value[0], value[1], value[2],))
    pool3.close()
    pool3.join()
    if q.qsize() > 0:  # 当queue的size大于0的话, 那就是进程里面出现了错误, raise, 结束任务
      log.error('save danmakus to DB occurs error')
      raise Exception(q)

    for item in red.keys('program-temp-*'):  # 删除为了剔除程序中的重复danmaku_id而存储的keys
      red.delete(item)
    log.info('[Delete] redis temp')
    log.info('[Done] save danmaku to DB')
    log.info('[DONE] analyze spiders\' data')
  except BaseException as e:
    raise e

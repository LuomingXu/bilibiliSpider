import math
import multiprocessing
import traceback
from datetime import datetime
from datetime import timezone, timedelta
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from typing import List, MutableMapping, Set

from bs4 import BeautifulSoup
from sqlalchemy.engine import ResultProxy

import online
from config import DBSession, engine, log
from danmaku.DO import DanmakuDO, DanmakuRealationDO, AVCidsDO
from danmaku.Entity import CustomTag
from local_processing.Entity import CustomFile, FileType


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


def save_cid_aid_relation(cid_aid: MutableMapping[int, int]):
  objs: List[AVCidsDO] = []
  conn = engine.connect()
  session = DBSession()

  sql: str = 'select cid from av_cids where cid in (%s)' % ','.join('%s' % item for item in cid_aid.keys())

  cids: ResultProxy = conn.execute(sql)
  for item in cids.fetchall():
    cid_aid.pop(item[0])
  conn.close()

  for cid, aid in cid_aid.items():
    obj: AVCidsDO = AVCidsDO()
    obj.cid = cid
    obj.aid = aid
    objs.append(obj)

  session.bulk_save_objects(objs)


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
    relationMap[relation.danmaku_id] = relation

  session = DBSession()
  try:
    removeExist(danmakuMap, relationMap)

    if danmakuMap.__len__() == relationMap.__len__() and relationMap.__len__() == 0:
      return

    session.bulk_save_objects(danmakuMap.values() if danmakuMap.values().__len__() > 0 else None)
    session.bulk_save_objects(relationMap.values() if relationMap.values().__len__() > 0 else None)
    session.commit()
  except Exception as e:
    session.rollback()
    print(e)
  else:
    print('Saved success')
  finally:
    session.close()
    print('[SAVED] danmakuMap.len: %s' % danmakuList.__len__())
    print('[SAVED] relationMap.len: %s' % relationMap.__len__())
    danmakuList.clear()
    relationMap.clear()


def removeExist(danmakuMap: MutableMapping[int, DanmakuDO],
                relationMap: MutableMapping[int, DanmakuRealationDO]):
  if danmakuMap.__len__() != relationMap.__len__():
    raise BaseException('length is not match')

  conn = engine.connect()

  sql: str = 'select danmaku_id from cid_danmaku where danmaku_id in (\'\', %s)' % (
    ', '.join('%s' % item for item in relationMap.keys()))

  ids: ResultProxy = conn.execute(sql)
  for item in ids.fetchall():
    relationMap.pop(item[0])

  sql = 'select id from danmaku where id in (\'\', %s)' % (
    ', '.join('%s' % str(item) for item in danmakuMap.keys()))

  ids = conn.execute(sql)
  for item in ids.fetchall():
    danmakuMap.pop(item[0])

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

  try:
    pool = Pool(processes = cpu_use_number)
    for item in res:
      value = item.get()
      pool.apply_async(func = save_danmaku_to_db, args = (value[0],))
      save_cid_aid_relation(value[1])
    pool.close()
    pool.join()
    log.info('[Done] DB')
  except Exception as e:
    log.exception(e)

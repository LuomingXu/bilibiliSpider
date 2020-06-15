import math
import multiprocessing
import os
import shutil
import traceback
from datetime import datetime, timezone, timedelta
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult
from queue import Queue
from typing import MutableMapping
from typing import Set, List

import selfusepy
from sqlalchemy.engine import ResultProxy

import _s3
import local_processing
from config import log, DBSession, cpu_use_number
from online import AV, AVInfoDO, AVStatDO


def analyze(q: Queue, data: MutableMapping[str, AV]) -> (List[AVInfoDO], List[AVStatDO]):
  infos: List[AVInfoDO] = []
  stats: List[AVStatDO] = []
  try:
    for file_name, obj in data.items():
      l: List[str] = os.path.basename(file_name).split(".")
      time_ns = int(l[0])
      get_data_time = datetime.fromtimestamp(time_ns / 1000_000_000, timezone(offset = timedelta(hours = 8)))
      log.info("[Analyze] top avs data: %s" % get_data_time.isoformat())
      for i, item in enumerate(obj.onlineList):
        avInfoDO = AVInfoDO(item)
        avStatDO = AVStatDO(item, i + 1, get_data_time)
        infos.append(avInfoDO)
        stats.append(avStatDO)
  except BaseException as e:
    name = multiprocessing.current_process().name
    _map: MutableMapping[str, str] = {name: traceback.format_exc()}
    q.put(_map)
    print('Oops: ', name)
  finally:
    return infos, stats


def read_file(dir: str, _map: MutableMapping[str, AV] = None) -> MutableMapping[str, AV]:
  if _map is None:
    _map = {}

  dir_or_files = os.listdir(dir)
  for item in dir_or_files:
    if not item.startswith("."):
      current_path = dir + item
      if os.path.isdir(current_path):
        current_path += "/"
        read_file(current_path, _map)
      else:
        s: str = open(current_path, "r", encoding = "utf-8").read()
        _map[current_path] = selfusepy.parse_json(s, AV())

  return _map


def main():
  """
  测试需要调整数据库, s3删除, archive目录
  :return:
  """
  temp_file_dir = 'data-temp/'

  # download data
  log.info("Getting objects' keys")
  keys: Set[str] = _s3.get_all_objects_key()

  if keys.__len__() < 1:
    log.info("No file in COS!")
    exit(0)
  else:
    local_processing.multi_download(temp_file_dir, keys)
    _s3.delete_objects(keys)
    log.info("Download files, DONE.")

  # reading data
  all_data: MutableMapping[str, AV] = read_file(temp_file_dir)

  log.info("Analyze")
  # multi analyze
  pool = Pool(processes = cpu_use_number)
  q = multiprocessing.Manager().Queue()

  size = int(math.ceil(all_data.__len__() / float(cpu_use_number)))
  map_temp: MutableMapping[str, AV] = {}

  res: List[ApplyResult] = list()
  for key, value in all_data.items():
    map_temp[key] = value
    if map_temp.__len__() % size == 0:
      res.append(pool.apply_async(func = analyze, args = (q, map_temp,)))
      map_temp = {}
  res.append(pool.apply_async(func = analyze, args = (q, map_temp,)))
  pool.close()
  pool.join()
  if q.qsize() > 0:  # 当queue的size大于0的话, 那就是进程里面出现了错误, raise, 结束任务
    log.error('analyze occurs error')
    raise Exception(q)

  # saving
  all_avinfos: List[AVInfoDO] = []
  all_avstats: List[AVStatDO] = []
  for item in res:
    v = item.get()
    all_avinfos.extend(v[0])
    all_avstats.extend(v[1])

  # remove avinfos which exist in db already and same in program
  log.info("Remove duplicated avinfo")
  temp: Set[int] = set()  # db
  for item in all_avinfos:
    temp.add(item.aid)
  session = DBSession()
  sql: str = "select aid from av_info where aid in (%s)" % ",".join("%s" % item for item in temp)
  aids: ResultProxy = session.execute(sql)
  temp.clear()
  for item in aids.fetchall():
    temp.add(int(item[0]))

  temp2: List[AVInfoDO] = []  # program
  for item in all_avinfos:
    if not temp.__contains__(item.aid):
      temp2.append(item)
      temp.add(item.aid)
  all_avinfos = temp2

  # db
  log.info("Save infos(%s) and stats(%s)" % (all_avinfos.__len__(), all_avstats.__len__()))
  session.bulk_save_objects(all_avinfos)
  session.bulk_save_objects(all_avstats)
  session.commit()

  # archive
  log.info("Archive")
  for item in all_data.keys():
    index: int = item.find("/online")
    shutil.move(item[:index], "D:/spider archive")

  log.info('[Done]')

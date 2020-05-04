import os
from datetime import datetime, timezone, timedelta
from typing import MutableMapping
from typing import Set, List

import selfusepy

import _file
import _s3
import local_processing
from config import log, DBSession
from online import AV, AVInfoDO, AVStatDO


def read_file(dir: str, _map: MutableMapping[int, AV] = None) -> MutableMapping[int, AV]:
  if _map is None:
    _map = {}
  dir_or_files = os.listdir(dir)
  for item in dir_or_files:
    current_path = '%s/%s' % (dir, item)
    if os.path.isdir(current_path):
      read_file(current_path, _map)
    else:
      l: List[str] = item.split('.')
      file_name = l[0]
      s: str = open(current_path, "r", encoding = "utf-8").read()
      create_time = int(file_name)
      _map[create_time] = selfusepy.parse_json(s, AV())

  return _map


def main():
  temp_file_dir = 'data-temp/'
  temp_file_dir = 'C:/Users/LuomingPC/Desktop/temp/'

  # download data
  log.info("Getting objects' keys")
  keys: Set[str] = _s3.get_all_objects_key()

  if keys.__len__() < 1:
    log.info("No files in COS!")
  else:
    local_processing.multi_download(temp_file_dir, keys)
    _s3.delete_objects(keys)
    log.info("Download files, DONE.")

  # reading data
  all_data: MutableMapping[int, AV] = read_file(temp_file_dir)

  # save
  exist_aids: Set[int] = set()
  save_succeed_filename: Set[int] = set()
  for file_name, obj in all_data.items():
    get_data_time = datetime.fromtimestamp(file_name / 1000_000_000, timezone(offset = timedelta(hours = 8)))
    log.info("[Saving] top avs data: %s" % get_data_time.isoformat())
    session = DBSession()
    for i, item in enumerate(obj.onlineList):
      avInfoDO = None
      avStatDO = AVStatDO(item, i + 1, get_data_time)

      if exist_aids.__contains__(avStatDO.aid):
        exist = True
      else:
        avInfoDO = AVInfoDO(item)
        exist = session.query(AVInfoDO).filter(AVInfoDO.aid == avInfoDO.aid).first()

      """
      存在则只添加关于av的statistic
      """
      try:
        if not exist:
          session.add(avInfoDO)
          session.add(avStatDO)
          log.info('[INSERT] aid: %s' % avInfoDO.aid)
        else:
          session.add(avStatDO)
          log.info('[UPDATE] av statistics, aid: %s' % avStatDO.aid)

        session.commit()
      except BaseException as e:
        session.rollback()
        raise e
      else:
        log.info("[Update or Insert] success")
    save_succeed_filename.add(file_name)

  _file.save(save_succeed_filename.__str__(), temp_file_dir + "saved.txt")

  log.info("Done!")

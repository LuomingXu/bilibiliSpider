import os
import shutil
from datetime import datetime, timezone, timedelta
from typing import MutableMapping
from typing import Set, List

import selfusepy

import _file
import _s3
import local_processing
from config import log, DBSession
from online import AV, AVInfoDO, AVStatDO


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
  temp_file_dir = 'data-temp/'

  # download data
  log.info("Getting objects' keys")
  keys: Set[str] = _s3.get_all_objects_key()

  if keys.__len__() < 1:
    log.info("No file in COS!")
  else:
    local_processing.multi_download(temp_file_dir, keys)
    _s3.delete_objects(keys)
    log.info("Download files, DONE.")

  # reading data
  all_data: MutableMapping[str, AV] = read_file(temp_file_dir)

  # save
  exist_aids: Set[int] = set()
  save_succeed_filename: Set[str] = set()

  try:
    for file_name, obj in all_data.items():
      l: List[str] = os.path.basename(file_name).split(".")
      time_ns = int(l[0])
      get_data_time = datetime.fromtimestamp(time_ns / 1000_000_000, timezone(offset = timedelta(hours = 8)))
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
        存在则只添加statistic
        """
        try:
          if not exist:
            session.add(avInfoDO)
            session.add(avStatDO)
            log.info('[INSERT] aid: %s' % avInfoDO.aid)
          else:
            exist_aids.add(avStatDO.aid)
            session.add(avStatDO)
            log.info('[UPDATE] av statistics, aid: %s' % avStatDO.aid)

          session.commit()
        except BaseException as e:
          session.rollback()
          raise e
        else:
          log.info("[Update or Insert] success")
      index: int = file_name.find("/online")
      save_succeed_filename.add(file_name[:index])
  except BaseException as e:
    raise e
  finally:
    # save
    _file.save(save_succeed_filename.__str__(), temp_file_dir + ".saved.txt")
    for item in save_succeed_filename:
      shutil.move(item, "D:/spider archive")

  log.info("Done!")

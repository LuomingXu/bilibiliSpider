import os
import shutil
from datetime import datetime, timezone, timedelta
from typing import MutableMapping, Set

import _s3
import multi_danmaku_v2
from config import log
from local_processing.Entity import CustomFile, FileType


def all_files(path: str, _map: MutableMapping[str, CustomFile] = None) -> MutableMapping[str, CustomFile]:
  if _map is None:
    _map = {}
  dir_or_files = os.listdir(path)
  for item in dir_or_files:
    current_path = '%s/%s' % (path, item)
    if os.path.isdir(current_path):
      all_files(current_path, _map)
    else:
      item = item.split('.')[0]
      try:
        if item.__len__() > 19:
          arr = item.split('-')
          _map[item] = CustomFile(item, open(current_path, 'r', encoding = 'utf-8').read(),
                                  FileType.Danmaku,
                                  datetime.fromtimestamp(int(arr[2]) / 1_000_000_000, timezone(timedelta(hours = 8))),
                                  aid = int(arr[0]), cid = int(arr[2]))
        else:
          _map[item] = CustomFile(item, open(current_path, 'r', encoding = 'utf-8').read(),
                                  FileType.Online,
                                  datetime.fromtimestamp(int(item) / 1_000_000_000, timezone(timedelta(hours = 8))))

      except Exception:
        pass  # 有一个占位文件, package-info.py会引发int()转化错误

  return _map


def gen_objectKeys_from_dir(_dir: str, keys: Set[str] = None):
  if keys is None:
    keys = set()
  dir_or_files = os.listdir(_dir)
  for item in dir_or_files:
    current_path = '%s/%s' % (_dir, item)
    if os.path.isdir(current_path):
      gen_objectKeys_from_dir(current_path, keys)
    else:
      abspath = os.path.abspath(current_path).replace('\\', '/')
      i = abspath.find('data-temp')
      keys.add(str(abspath[i:]).replace('data-temp/', ''))
  return keys


def main():
  temp_file_dir = 'data-temp/'
  keys: Set[str] = _s3.get_all_objects_key()
  _s3.download_objects(temp_file_dir, keys)
  for _dir in os.listdir(temp_file_dir):
    _dir = temp_file_dir + _dir + '/'
    dir_keys: Set[str] = gen_objectKeys_from_dir(_dir)
    log.info('Analyze dir: %s' % _dir)
    try:
      _map = all_files(_dir)
      log.info('Waiting to process, files len: %s' % _map.__len__())
      multi_danmaku_v2.main(_map)  # analyze
    except Exception as e:
      log.error('dir: %s occurs error' % _dir)
      raise e
    else:
      shutil.rmtree(_dir, ignore_errors = True)  # 处理完毕, 删除temp文件
      log.info('Delete temp files done')
      _s3.delete_objects(dir_keys)
      log.info('Delete objects done')

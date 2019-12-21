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


def main():
  file_temp_dir = 'data-temp/'
  # keys: Set[str] = _s3.get_all_objects_key()
  # _s3.download_objects(file_temp_dir, keys)
  _map = all_files(file_temp_dir)
  log.info('Waiting to process, len: %s' % _map.__len__())
  multi_danmaku_v2.main(_map)  # analyze
  # shutil.rmtree(file_temp_dir, ignore_errors = True)  # 处理完毕, 删除temp文件
  # log.info('Delete temp files done')

  # todo 暂时不需要删除 _s3.delete_objects(keys)

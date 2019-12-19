import multi_danmaku
import online
import user
import os
import shutil
import _minio
import danmaku
from typing import MutableMapping

if __name__ == '__main__':
  dirs: list = ['data-temp/danmaku', 'data-temp/online']
  for dir in dirs:
    os.makedirs(dir, exist_ok = True)

  waiting_upload_files: MutableMapping[str, str] = {}

  res = online.getting_data()
  waiting_upload_files.update(res[0])  # online
  # user.__main__(res[2])  # owner
  # multi_danmaku.main(res[1])  # multi danmaku
  waiting_upload_files.update(danmaku.getting_data(res[1]))  # danmaku

  _minio.put(waiting_upload_files)

  for dir in dirs:
    shutil.rmtree(dir, ignore_errors = True)  # 不管存在与否, 空与否都能删了

  print('done')

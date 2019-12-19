import multiprocessing
import os
import shutil
import time
from datetime import datetime, timezone, timedelta
from typing import MutableMapping

import _minio
import config
import danmaku
import online
import user
from config import log

if __name__ == '__main__':
  delta = 30 * 60 * 1000_000_000  # request delta time 30min
  last_request_time = 0

  try:
    while True:
      if time.time_ns() - last_request_time >= delta:
        if multiprocessing.cpu_count() <= 100:
          """
          在性能不足的服务器上进行爬虫的工作, 保存获取的数据到oss
          """
          log.info('[Spider start]')
          last_request_time = time.time_ns()
          config.date = datetime.now(timezone(timedelta(hours = 8))).strftime('%Y-%m-%d_%H-%M-%S')

          dirs: list = ['data-temp/%s/danmaku' % config.date, 'data-temp/%s/online' % config.date]
          for dir in dirs:
            os.makedirs(dir, exist_ok = True)  # create temp files' dir

          waiting_upload_files: MutableMapping[str, str] = {}

          res = online.getting_data()
          waiting_upload_files.update(res[0])  # online
          user.__main__(res[2])  # owner
          waiting_upload_files.update(danmaku.getting_data(res[1]))  # danmaku

          _minio.put(waiting_upload_files)  # save to oss

          for dir in dirs:
            shutil.rmtree(dir, ignore_errors = True)  # 不管存在与否, 空与否都能删了

          log.info('[Spider end]')
        else:
          """
          在本机上进行数据的处理, 充分利用3700x😁
          """
          # todo 利用多核晚上数据处理
          pass
      else:
        time.sleep(5)
  except Exception as e:
    """
    异常报告    
    """
    # todo
    pass

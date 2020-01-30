import os
import platform
import shutil
import time
from datetime import datetime, timezone, timedelta
from typing import MutableMapping

from selfusepy.utils import eprint

import _email
import _s3
import _user
import config
import danmaku
import local_processing
import online
from config import log, regular_spider_delta, quick_spider_delta, night_spider_delta, \
  regular_set, quick_set, night_set, email_to_addr, red


def set_req_delta(hour: int) -> int:
  if regular_set.__contains__(hour):
    return regular_spider_delta
  elif quick_set.__contains__(hour):
    return quick_spider_delta
  elif night_set.__contains__(hour):
    return night_spider_delta


if __name__ == '__main__':
  try:
    if platform.system() == 'Windows':
      """
      在本机上进行数据的处理, 充分利用3700x😁
      """
      local_processing.main()
      exit(0)
    else:
      """
      在性能不足的服务器上进行爬虫的工作, 保存获取的数据到cos
      """
      delta = set_req_delta(datetime.now(timezone(timedelta(hours = 8))).hour)
      last_request_time = red.get('last_request_time')
      if last_request_time:
        last_request_time = int(last_request_time)
      else:
        last_request_time = 0

      while True:
        if time.time_ns() - last_request_time >= delta:
          log.info(
            '[Spider start] last request time: %s' % datetime.fromtimestamp(int(last_request_time) / 1_000_000_000,
                                                                            timezone(timedelta(hours = 8))))

          last_request_time = time.time_ns()
          red.set('last_request_time', last_request_time)

          now = datetime.now(timezone(timedelta(hours = 8)))
          config.date = now.strftime('%Y-%m-%d_%H-%M-%S')
          delta = set_req_delta(now.hour)  # set req delta time by current hour

          dirs: list = ['data-temp/%s/danmaku' % config.date, 'data-temp/%s/online' % config.date]
          for _dir in dirs:
            os.makedirs(_dir, exist_ok = True)  # create temp files' dir

          waiting_upload_files: MutableMapping[str, str] = {}

          res = online.getting_data()
          waiting_upload_files.update(res[0])  # online
          _user.__main__(res[2])  # owner
          waiting_upload_files.update(danmaku.getting_data(res[1]))  # danmaku

          _s3.put(waiting_upload_files)  # save to oss

          shutil.rmtree('data-temp/%s' % config.date, ignore_errors = True)  # 不管存在与否, 空与否都能删了

          log.info('[Spider end]')
        else:
          time.sleep(1)
  except BaseException as e:
    """
    异常报告    
    """
    if isinstance(e, SystemExit):
      """
      exit() 函数是通过raise SystemExit异常来退出程序, 此Exception不需要捕获
      """
      pass
    else:
      log.exception(e)
      import traceback, multiprocessing

      flag = False
      for item in e.args:
        if issubclass(type(item), multiprocessing.managers.BaseProxy):
          flag = True
          s: str = ''
          for i in range(item.qsize()):
            for key, value in item.get().items():
              s += key + value
            s += '\n'
          eprint(s)
          _email.send(email_to_addr, s)
      if not flag:
        _email.send(email_to_addr, traceback.format_exc())

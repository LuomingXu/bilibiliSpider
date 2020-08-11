import multiprocessing
import time

from config import log


def consumer():
  r = ''
  t = ''
  while True:
    n = yield r
    m = yield t
    if not n:
      return
    log.info('[CONSUMER] Consuming %s...' % n)
    log.info('[CONSUMER] Consuming %s...' % m)
    r = '200 OK'


def produce(c):
  c.send(None)
  n = 0
  while n < 5:
    n = n + 1
    log.info('[PRODUCER] Producing %s...' % n)
    c.send(n)
    r = c.send(n + 1)
    log.info('[PRODUCER] Consumer return: %s' % r)
    log.info('sleep')
    time.sleep(5)
  c.close()


count = 0


async def hello(start_time: int):
  global count
  log.info('i: %s, start' % count)

  deleta = start_time + count * 2 - int(time.time())
  time.sleep(deleta if deleta > 0 else 0)
  count += 1

  log.info('io start')
  await asyncio.sleep(5)
  log.info('io done')


async def io():
  log.info('io')
  time.sleep(5)
  import asyncio
  await asyncio.sleep(5)


def func(cid: int):
  print(multiprocessing.current_process().name + str(cid))


def fig(n: int):
  dp: dict = {k: 0 for k in range(1, n + 2)}
  dp[1] = dp[2] = 1
  for i in range(3, n + 1):
    dp[i] = dp[i - 1] + dp[i - 2]
  return dp[n]


if __name__ == '__main__':
  # import asyncio
  # loop = asyncio.get_event_loop()
  # start_time: int = int(time.time())
  # tasks = list()
  # tasks.append(hello(start_time))
  # tasks.append(hello(start_time))
  # loop.run_until_complete(asyncio.wait(tasks))
  # loop.close()
  # exit(0)

  from _s3 import s3_client

  import _s3
  # print(_s3.abort_part_upload("test.7z", "3cb281ad-6718-4a1f-9243-82ba1ef820ae"))
  res = _s3.part_upload("C:/Users/MyCompanyDesktop/Desktop/test.7z", "test.7z")
  print("main %s" % res)
  exit(0)

  from subprocess import Popen
  import subprocess

  res = subprocess.run(["/usr/bin/bash", "pwd"], shell = True)
  print(res)
  exit(0)

  from config import DBSession, engine
  from danmaku.DO import AVCidsDO
  from danmaku.Entity import AvDanmakuCid

  values: list = list()
  obj: AvDanmakuCid = AvDanmakuCid()
  obj.cid = 142953222
  obj.pagename = '\u3010\u306f\u3058\u3081\u3057\u3083\u3061\u3087\u30fc\u3011Hajime\u793e\u957f \u5982\u679c\u73ed\u91cc\u5168\u90e8\u90fd\u662f\u7a7f\u7740\u6cf3\u88c5\u7684\u5973\u5b69\u5b50\uff0c\u8003\u8bd5\u5206\u6570\u4f1a\u4e0a\u5347\uff1f\u4e0b\u964d\uff1f'
  obj.page = 1
  values.append(obj)
  obj = AvDanmakuCid()
  obj.cid = 143185245
  obj.pagename = '286\u6307\u73af\u738b-1B\u7ad9'
  obj.page = 1
  values.append(obj)

  session = DBSession()

  try:
    l: list = list()
    for item in values:
      param = {'av_cids_cid': item.cid, 'page': item.page, 'pagename': item.pagename}
      l.append(param)

    session.bulk_update_mappings(AVCidsDO, l)
  except BaseException:
    import traceback

    traceback.print_exc()
  else:
    print('success')
  exit(0)
  f = open('data-temp/2020-01-06_21-44-53/danmaku/75958759.json', 'r', encoding = 'utf-8')
  s = f.read()
  from danmaku.Entity import AvDanmakuCid
  import selfusepy
  from typing import List, MutableMapping

  l: List[AvDanmakuCid] = selfusepy.parse_json_array(s, AvDanmakuCid())
  # sql: str = '\n'.join(
  #   'update av_cids set page = %s, page_name = %s where cid = %s;' % (item.page, item.pagename, item.cid) for item in l)
  # print(sql)
  _map: MutableMapping[int, AvDanmakuCid] = {}
  for item in l:
    _map[item.cid] = item

  print(_map)
  exit(0)
# t = time.time()
# print(int(round(time.time()*1000)))
# time.sleep(0.1)
# print(int(round(time.time()*1000)))

# loop = asyncio.get_event_loop()
# start_time: int = int(time.time())
# tasks = [hello(start_time), hello(start_time), hello(start_time), hello(start_time), hello(start_time)]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()

# c = consumer()
# produce(c)

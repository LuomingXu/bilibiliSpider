import json
from typing import MutableMapping, Set

from redis.client import Redis

red = Redis(db = 2)


def delete_all():
  red = Redis()
  for key in red.keys():
    red.delete(key)


def increment():
  red = Redis()
  print(red.get('key') is None)
  red.set('key', 1)
  red.incr('key', 2)


from datetime import datetime, timedelta, timezone


def judge_req_times():
  temp1 = 0
  temp2 = 0
  while True:
    cid_len = yield temp1
    print(cid_len)
    times = yield temp2
    print(times)
    if cid_len <= 3:
      return 'False'
    elif cid_len <= 10:
      return (times >= 6).__str__()
    return (times >= 3).__str__()


def is_req_danmaku(cid_len: int, aid: int, judge) -> bool:
  judge.send(None)
  judge.send(cid_len)
  r: bool
  key = str(aid.__str__() + '-req-times')
  res = red.get(key)
  if res is None:
    red.set(key, 1)
    r = judge.send(1)
  else:
    res = int(res)
    print('aid: %s, req times: %s' % (aid, res))
    r = judge.send(res)
    print(r)
    if not r:
      red.incr(key, 1)
  judge.close()
  return r

def consumer():
  r = 0
  temp = 0
  while True:
    n = yield r
    n2 = yield temp
    if not n:
      return
    print('[CONSUMER] Consuming %s...' % n)
    print('[CONSUMER] Consuming %s...' % n2)
    r = '200 OK'


def produce(c, i:int, j:int):
  c.send(None)
  n = 0
  while n < 5:
    n = n + 1
    print('[PRODUCER] Producing %s...' % i)
    c.send(j)
    print('[PRODUCER] Producing %s...' % j)
    r = c.send(i)
    print('[PRODUCER] Consumer return: %s' % r)
  c.close()



if __name__ == '__main__':

  l1 = [1, 2, 3, 4, 9, 10, 11, 12]
  l2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
  for item1 in l1:
    for item2 in l2:
      j = judge_req_times()
      is_req_danmaku(item2, item1, j)
      # c = consumer()
      # produce(c, item2, item1)

  s: Set[int] = {1, 2, 3}
  date: datetime = datetime.now(timezone(timedelta(hours = 8)))
  print(date.hour)
  print(date.hour < 10)

  increment()

  # count = 0
  # for key in red.keys():
  #   count += len(red.smembers(key))
  # print(count)

  _map: MutableMapping[int, Set[int]] = {}
  d: list = json.loads(open('C:\\Users\\LuomingPC\\Desktop\\cloud_cid_danmaku.json', 'r', encoding = 'utf-8').read())
  print(d.__len__())
  for item in d:
    if _map.get(item['cid']) is None:
      _map[item['cid']] = set()
      _map[item['cid']].add(item['danmaku_id'])
    else:
      _map[item['cid']].add(item['danmaku_id'])

  for cid, danmakuIds in _map.items():
    red.sadd(cid, *danmakuIds)

import json
from typing import MutableMapping, Set

from redis.client import Redis

def delete_all():
  red= Redis()
  for key in red.keys():
    red.delete(key)

def increment():
  red = Redis()
  print(red.get('key') is None)
  red.set('key', 1)
  red.incr('key', 2)
from datetime import datetime, timedelta, timezone

if __name__ == '__main__':
  s: Set[int] = {1, 2, 3}
  date: datetime = datetime.now(timezone(timedelta(hours = 8)))
  print(date.hour)
  print(date.hour < 10)

  increment()

  red = Redis()
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

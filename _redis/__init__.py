import json
from typing import MutableMapping, Set

from redis.client import Redis

if __name__ == '__main__':

  red = Redis()
  count = 0
  for key in red.keys():
    count += len(red.smembers(key))
  print(count)

  _map: MutableMapping[int, Set[int]] = {}
  d: list = json.loads(open('C:\\Users\\LuomingPC\\Desktop\\cloud_cid_danmaku.json', 'r', encoding = 'utf-8').read())
  for item in d:
    if _map.get(item['cid']) is None:
      _map[item['cid']] = set()
      _map[item['cid']].add(item['danmaku_id'])
    else:
      _map[item['cid']].add(item['danmaku_id'])

  for cid, danmakuIds in _map.items():
    red.sadd(cid, *danmakuIds)

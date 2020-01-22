import collections
import json
from typing import List, MutableMapping, Counter


def delete_duplicate_av_stat():
  """
  去除av stat中重复的数据记录
  :return:
  """
  f = open('C:/Users/LuomingPC/Desktop/bilibili_av_stat.json', 'r', encoding = "utf-8")
  s = f.read()

  arr: list = json.loads(s)
  arr.sort(key = lambda k: k['aid'])
  l: MutableMapping[int, str] = {}
  for item in arr:
    _id = item['id']
    aid = item['aid']
    view = item['view']
    l[_id] = ('%s-%s' % (aid, view))

  c: Counter[str] = collections.Counter(l.values())
  temp: List[int] = list()
  for item in c:
    count = c[item]
    if count >= 2:
      for key, value in l.items():
        if value == item:
          count -= 1
          if count == 0:
            break
          temp.append(key)
  print('delete from av_stat where id in (%s)' % ','.join('%s' % item for item in temp))

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


# algorithm from https://www.zhihu.com/question/381784377/answer/1099438784
table: str = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr: dict = {}
for i in range(58):
  tr[table[i]] = i
s: List[int] = [11, 10, 3, 8, 4, 6]
xor: int = 177451812
add: int = 8728348608


def bv2av(x: str) -> int:
  r: int = 0
  for i in range(6):
    r += tr[x[s[i]]] * 58 ** i
  return (r - add) ^ xor


def av2bv(x: int) -> str:
  x: int = (x ^ xor) + add
  r: list = list('BV1  4 1 7  ')
  for i in range(6):
    r[s[i]] = table[x // 58 ** i % 58]
  return ''.join(r)

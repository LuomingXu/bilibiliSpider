import selfusepy
from typing import List, MutableMapping
from bs4 import BeautifulSoup
from db import DBSession, engine
from selfusepy.utils import Logger
from selfusepy import HTTPResponse
from online.AVDO import AVInfoDO
from bs4 import Tag
from datetime import timezone, timedelta, datetime
from danmaku.DanmakuDO import DanmakuDO, DanmakuRealationDO
from sqlalchemy.engine import ResultProxy


def removeExist(cid: int, danmakuMap: MutableMapping[int, DanmakuDO],
                relationMap: MutableMapping[int, DanmakuRealationDO]):
  if danmakuMap.__len__() != relationMap.__len__():
    raise BaseException('length is not match')

  sql: str = 'select danmaku_id from cid_danmaku where danmaku_id in (%s) and cid = %s' % (
    ', '.join('%s' % str(item) for item in relationMap.keys()), cid)

  conn = engine.connect()
  ids: ResultProxy = conn.execute(sql)
  for item in ids.fetchall():
    relationMap.pop(item[0])

  sql = 'select id from danmaku where id in (%s)' % (
    ', '.join('%s' % str(item) for item in danmakuMap.keys()))

  ids = conn.execute(sql)
  for item in ids.fetchall():
    danmakuMap.pop(item[0])

  conn.close()


if __name__ == '__main__':
  session = DBSession()
  log = Logger("error.log").logger
  chromeUserAgent: dict = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

  avInfos: List[AVInfoDO] = session.query(AVInfoDO).all()
  for avInfo in avInfos:
    res: HTTPResponse = selfusepy.get('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(avInfo.cid))
    soup: BeautifulSoup = BeautifulSoup(markup = str(res.data, encoding = 'utf-8').replace('\\n', ''),
                                        features = 'lxml')
    danmakus: List[Tag] = soup.find_all(name = 'd')
    danmakuMap: MutableMapping[int, DanmakuDO] = {}
    relationMap: MutableMapping[int, DanmakuRealationDO] = {}
    for danmaku in danmakus:
      # 弹幕出现时间,模式,字体大小,颜色,发送时间戳,弹幕池,用户Hash,数据库ID
      obj: DanmakuDO = DanmakuDO()
      obj.content = danmaku.text
      l: list = str(danmaku['p']).split(',')
      obj.danmaku_epoch = float(l[0])
      obj.mode = int(l[1])
      obj.font_size = int(l[2])
      obj.font_color = int(l[3])
      obj.send_time = datetime.fromtimestamp(int(l[4]), timezone(timedelta(hours = 8)))
      obj.danmaku_pool = int(l[5])
      obj.user_hash = int(l[6], 16)
      obj.id = int(l[7])

      relation: DanmakuRealationDO = DanmakuRealationDO()
      relation.cid = avInfo.cid
      relation.danmaku_id = obj.id

      danmakuMap[obj.id] = obj
      relationMap[relation.danmaku_id] = relation

    try:
      removeExist(avInfo.cid, danmakuMap, relationMap)

      if danmakuMap.__len__() == relationMap.__len__() and relationMap.__len__() == 0:
        print('cid:', avInfo.cid, 'has saved all danmaku')
        continue

      session.bulk_save_objects(danmakuMap.values() if danmakuMap.values().__len__() > 0 else None)
      session.bulk_save_objects(relationMap.values() if relationMap.values().__len__() > 0 else None)
      session.commit()
    except Exception as e:
      session.rollback()
      log.exception(e)
      log.error('cid: %s, has error. ' % avInfo.cid)
    else:
      print('cid:', avInfo.cid, '. Done.')
    finally:
      print('danmakuMap.len:', danmakuMap.__len__())
      print('relationMap.len:', relationMap.__len__())
      danmakuMap.clear()
      relationMap.clear()

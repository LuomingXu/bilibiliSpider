from datetime import timezone, timedelta, datetime
from typing import List, MutableMapping, Set

import crc32
import json
import selfusepy
import time
from bs4 import BeautifulSoup
from bs4 import Tag
from selfusepy import HTTPResponse
from sqlalchemy.engine import ResultProxy

from danmaku.DO import DanmakuDO, DanmakuRealationDO, AVCidsDO
from danmaku.Entity import AvDanmakuCid
from db import DBSession, engine, log
from online.AVDO import AVInfoDO


def removeExist(cid: int, danmakuMap: MutableMapping[int, DanmakuDO],
                relationMap: MutableMapping[int, DanmakuRealationDO]):
  if danmakuMap.__len__() != relationMap.__len__():
    raise BaseException('length is not match')

  conn = engine.connect()

  sql: str = 'select danmaku_id from cid_danmaku where danmaku_id in (%s) and cid = %s' % (
    ', '.join('%s' % item for item in relationMap.keys()), cid)

  ids: ResultProxy = conn.execute(sql)
  for item in ids.fetchall():
    relationMap.pop(item[0])

  sql = 'select id from danmaku where id in (%s)' % (
    ', '.join('%s' % str(item) for item in danmakuMap.keys()))

  ids = conn.execute(sql)
  for item in ids.fetchall():
    danmakuMap.pop(item[0])

  conn.close()


def __main__():
  session = DBSession()

  chromeUserAgent: dict = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

  avInfos: List[AVInfoDO] = session.query(AVInfoDO).all()
  for i, avInfo in enumerate(avInfos):
    resAllCids: HTTPResponse = selfusepy.get('https://www.bilibili.com/widget/getPageList?aid=' + str(avInfo.aid))
    danmakuCids: List[AvDanmakuCid] = list()
    j = json.loads(resAllCids.data)
    log.info('Start. i: %s, aid: %s, cid length: %s' % (i, avInfo.aid, j.__len__()))
    if isinstance(json.loads(resAllCids.data), list):
      for item in j:
        danmakuCids.append(selfusepy.parse_json(json.dumps(item), AvDanmakuCid()))

    for j, cidE in enumerate(danmakuCids):
      avCid: AVCidsDO = session.query(AVCidsDO).filter_by(cid = cidE.cid).first()
      if avCid is None:
        log.info('av-cid relation Saving, aid: %s, cid: %s' % (avInfo.aid, cidE.cid))
        session.add(AVCidsDO(avInfo.aid, cidE))
        session.commit()
      else:
        log.info('av-cid relation Exist, aid: %s, cid: %s' % (avInfo.aid, cidE.cid))

      res: HTTPResponse = selfusepy.get('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(cidE.cid),
                                        head = chromeUserAgent)
      soup: BeautifulSoup = BeautifulSoup(markup = str(res.data, encoding = 'utf-8').replace('\\n', ''),
                                          features = 'lxml')
      danmakus: List[Tag] = soup.find_all(name = 'd')
      maxlimit: Tag = soup.find(name = 'maxlimit')

      conn = engine.connect()
      sql: str = 'select count(danmaku_id) from cid_danmaku where cid = %s' % cidE.cid
      count: int = int(conn.execute(sql).fetchone()[0])

      log.info('aid: %s, cid: %s, danmaku count: %s, max limit: %s' % (avInfo.aid, cidE.cid, count, maxlimit.text))
      if count >= int(maxlimit.text):
        log.info('j: %s, Continue. aid: %s, cid: %s not operate DB' % (j, avInfo.aid, cidE.cid))
        continue

      save_danmaku(cidE, danmakus)

      log.info('j: %s, cid: %s, aid: %s, danmaku\'s save danmakus sleep 3s.' % (j, cidE.cid, avInfo.aid))
      time.sleep(3)

    print('aid: %s, i: %s. danmaku Done.' % (avInfo.aid, i))


def save_danmaku(avDanmakuCid: AvDanmakuCid, danmakus: List[Tag]):
  session = DBSession()

  danmakuMap: MutableMapping[int, DanmakuDO] = {}
  relationMap: MutableMapping[int, DanmakuRealationDO] = {}
  log.info('cid: %s, danmakus: %s' % (avDanmakuCid.cid, danmakus.__len__()))
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
    # 暂不直接从数据库获取crc32数据, 太慢了
    # value = crc32.get_value(l[6])
    # if value[0] > 0:
    #   obj.user_id = value[1]
    obj.id = int(l[7])

    relation: DanmakuRealationDO = DanmakuRealationDO()
    relation.cid = avDanmakuCid.cid
    relation.danmaku_id = obj.id

    danmakuMap[obj.id] = obj
    relationMap[relation.danmaku_id] = relation

    if danmakuMap.__len__() % 1000 == 0:
      log.info('added map len: %s' % danmakuMap.__len__())

  try:
    removeExist(avDanmakuCid.cid, danmakuMap, relationMap)

    if danmakuMap.__len__() == relationMap.__len__() and relationMap.__len__() == 0:
      log.info('cid: %s, has saved all danmaku' % avDanmakuCid.cid)
      return

    session.bulk_save_objects(danmakuMap.values() if danmakuMap.values().__len__() > 0 else None)
    session.bulk_save_objects(relationMap.values() if relationMap.values().__len__() > 0 else None)
    session.commit()
  except Exception as e:
    session.rollback()
    log.exception(e)
    log.error('cid: %s, has error. ' % avDanmakuCid.cid)
  else:
    log.info('cid: %s, Saved into DB.' % avDanmakuCid.cid)
  finally:
    session.close()
    log.info('danmakuMap.len: %s' % danmakuMap.__len__())
    log.info('relationMap.len: %s' % relationMap.__len__())
    danmakuMap.clear()
    relationMap.clear()

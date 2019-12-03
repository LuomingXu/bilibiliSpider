import selfusepy
from typing import List
from bs4 import BeautifulSoup
from db import DBSession
from selfusepy.utils import Logger
from selfusepy import HTTPResponse
from online.AVDO import AVInfoDO
from bs4 import Tag
from datetime import timezone, timedelta, datetime
from danmaku.DanmakuDO import DanmakuDO, DanmakuRealationDO

if __name__ == '__main__':
  session = DBSession()
  log = Logger("error.log").logger
  chromeUserAgent: dict = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}

  avInfos: List[AVInfoDO] = session.query(AVInfoDO).all()
  for avInfo in avInfos:
    avInfo.cid = '132084205'
    res: HTTPResponse = selfusepy.get('https://api.bilibili.com/x/v1/dm/list.so?oid=' + str(avInfo.cid))
    soup: BeautifulSoup = BeautifulSoup(markup = str(res.data, encoding = 'utf-8').replace('\\n', ''),
                                        features = 'lxml')
    danmakus: List[Tag] = soup.find_all(name = 'd')
    danmakuList: List[DanmakuDO] = []
    relationList: List[DanmakuRealationDO] = []
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

      danmakuList.append(obj)
      relationList.append(relation)

      try:
        session.add(obj)
        session.add(relation)
        session.commit()
      except Exception as e:
        log.exception(e)
        print(obj)
        print(relation)
    #
    # session.bulk_save_objects(danmakuList)
    # session.bulk_save_objects(relationList)
    # session.commit()
    print('cid: ', avInfo.cid, '. Done.')

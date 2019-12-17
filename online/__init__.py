import re, selfusepy
from typing import List, Set
from bs4 import BeautifulSoup, Tag
from db import DBSession, log
from online.DO import AVInfoDO, AVStatDO
from online.Entity import OnlineList


def __main__() -> (List[int], Set[int]):
  chromeUserAgent: dict = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
  res = selfusepy.get(url = 'https://www.bilibili.com/video/online.html', head = chromeUserAgent)
  soup: BeautifulSoup = BeautifulSoup(markup = str(res.data, encoding = 'utf-8').replace('\\n', ''),
                                      features = 'lxml')
  aidList: List[int] = list()
  midSet: Set[int] = set()

  # 获取其中包含的json
  scripts: List[Tag] = soup.find_all(name = 'script')
  script: Tag = scripts.pop(5)  # 需要的script标签位于第五个
  pattern = re.compile(r'{([\s\S]*)\};')
  value = pattern.findall(script.prettify())
  temp = '{' + str(value[0]).replace('\\n', '') + '}'  # remove \n
  obj: OnlineList = selfusepy.parse_json(temp, OnlineList())

  session = DBSession()
  for item in obj.onlineList:
    aidList.append(item.aid)
    midSet.add(item.owner.mid)

    avInfoDO = AVInfoDO(item)
    avStatDO = AVStatDO(item)

    exist: AVInfoDO = session.query(AVInfoDO).filter_by(aid = avInfoDO.aid).first()
    if not exist:
      try:
        session.add(avInfoDO)
        session.add(avStatDO)
        session.commit()
        log.info('[INSERT] aid: %s' % avInfoDO.aid)
      except Exception as e:
        session.rollback()
        log.error('aid: %s. %s' % (avInfoDO.aid, e))
    else:
      try:
        session.add(avStatDO)
        session.commit()
        log.info('[UPDATE] [Statistics] aid: %s' % avInfoDO.aid)
      except Exception as e:
        session.rollback()
        log.exception(e)
        log.error('aid: %s. %s' % (avInfoDO.aid, e))

  session.close()
  log.info('Done')
  return aidList, midSet

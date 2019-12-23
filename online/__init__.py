import re
import time
from datetime import datetime
from typing import List, Set

import selfusepy
from bs4 import BeautifulSoup
from bs4.element import Tag

import _file
import config
from config import DBSession, log, chromeUserAgent
from online.DO import AVInfoDO, AVStatDO
from online.Entity import AV


def getting_data() -> ({str: str}, List[int], Set[int]):
  log.info('[START] Getting top AVs at bilibili.com')
  res = selfusepy.get(url = 'https://www.bilibili.com/video/online.html', head = chromeUserAgent)
  soup: BeautifulSoup = BeautifulSoup(markup = str(res.data, encoding = 'utf-8').replace('\\n', ''),
                                      features = 'lxml')

  # 获取其中包含的json
  scripts: List[Tag] = soup.find_all(name = 'script')
  script: Tag = scripts.pop(5)  # 需要的script标签位于第五个
  pattern = re.compile(r'{([\s\S]*)\};')
  value = pattern.findall(script.prettify())
  temp = '{' + str(value[0]).replace('\\n', '') + '}'  # remove \n
  file_name = '%s/online/%s.json' % (config.date, time.time_ns())
  file_path = 'data-temp/%s' % file_name
  _file.save(temp, file_path)

  # pre processing data
  aidList: List[int] = list()
  midSet: Set[int] = set()
  obj: AV = selfusepy.parse_json(temp, AV())
  for item in obj.onlineList:
    aidList.append(item.aid)
    midSet.add(item.owner.mid)

  log.info('[DONE] Getting data. [SLEEP] 2s')
  time.sleep(2)
  return {file_name: file_path}, aidList, midSet


def processing_data(j: str, get_data_time: datetime):
  obj: AV = selfusepy.parse_json(j, AV())
  log.info("[Saving] top avs data: %s" % get_data_time.isoformat())
  session = DBSession()
  for item in obj.onlineList:
    avInfoDO = AVInfoDO(item)
    avStatDO = AVStatDO(item, get_data_time)

    exist: AVInfoDO = session.query(AVInfoDO).filter(AVInfoDO.aid == avInfoDO.aid).first()

    """
    存在则只添加关于av的statistic
    """
    try:
      if not exist:
        session.add(avInfoDO)
        session.add(avStatDO)
        log.info('[INSERT] aid: %s' % avInfoDO.aid)
      else:
        session.add(avStatDO)
        log.info('[UPDATE] av statistics, aid: %s' % avInfoDO.aid)

      session.commit()
    except Exception as e:
      session.rollback()
      raise e
    else:
      log.info("[Update or Insert] success")

  session.close()
  log.info('[DONE] save top AVs')

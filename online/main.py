import re, json, time
from typing import List

from bs4 import BeautifulSoup, Tag
from datetime import datetime, timedelta, timezone

import selfusepy
from online.AV import AV
from online.AVDO import AVInfoDO, AVStatDO
from db import DBSession
from selfusepy.utils import Logger

if __name__ == '__main__':

  while True:
    chromeUserAgent: dict = {
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    log = Logger("error.log").logger
    res = selfusepy.get(url = 'https://www.bilibili.com/video/online.html', head = chromeUserAgent)

    soup: BeautifulSoup = BeautifulSoup(markup = str(res.data, encoding = 'utf-8').replace('\\n', ''),
                                        features = 'lxml')

    # 获取其中包含的json

    scripts: List[Tag] = soup.find_all(name = 'script')
    script: Tag = scripts.pop(5)  # 需要的script标签位于第五个
    pattern = re.compile(r'{([\s\S]*)\};')
    value = pattern.findall(script.prettify())
    temp = '{' + str(value[0]).replace('\\n', '') + '}'  # remove \n
    temp.replace('\\u002F', '/')
    obj: AV = selfusepy.parse_json(temp, AV())

    session = DBSession()
    fileName = 'AVList-%s.json' % (datetime.now(timezone(timedelta(hours = 8))).strftime('%Y-%m-%d-%H-%M-%S%z'))
    for item in obj.onlineList:
      avInfo = AVInfoDO(item)
      avStat = AVStatDO(item)

      # jsonTemp = json.loads(temp)['onlineList'].pop(0)
      #
      # print(jsonTemp['aid'])
      exist: AVInfoDO = session.query(AVInfoDO).filter_by(aid = avInfo.aid).first()
      if not exist:
        try:
          session.add(avInfo)
          session.add(avStat)
          session.commit()
        except Exception as e:
          session.rollback()
          fileName = 'AV-%s-%s.json' % (
            avInfo.aid, datetime.now(timezone(timedelta(hours = 8))).strftime('%Y-%m-%d-%H-%M-%S%z'))
          f = open(fileName, 'w', encoding = 'utf-8')
          f.write(avInfo.__str__() + '---' + avStat.__str__())
          log.error("error: %s, aid: %s" % (e, avInfo.aid))
      else:
        try:
          session.add(avStat)
          session.commit()
        except Exception as e:
          session.rollback()
          fileName = 'AV-%s-%s.json' % (
            avStat.aid, datetime.now(timezone(timedelta(hours = 8))).strftime('%Y-%m-%d-%H-%M-%S%z'))
          f = open(fileName, 'w', encoding = 'utf-8')
          f.write(avStat.__str__())
          log.exception(e)
          log.error("error: %s, aid: %s" % (e, avStat.aid))

    log.info('Done')
    time.sleep(30 * 60)

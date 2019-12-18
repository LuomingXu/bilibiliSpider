from datetime import datetime

from selfusepy.utils import override_str
from sqlalchemy import Column, BIGINT, DATETIME, String, INTEGER, DECIMAL
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

from danmaku.Entity import AvDanmakuCid

Base = declarative_base()


@override_str
class DanmakuRealationDO(Base):
  """
  cid与弹幕的关系
  """
  __tablename__ = 'cid_danmaku'

  cid = Column(BIGINT, primary_key = True)
  danmaku_id = Column(BIGINT)

  def __init__(self):
    self.cid = -1
    self.danmaku_id = -1


@override_str
class DanmakuDO(Base):
  """
  弹幕
  """
  __tablename__ = 'danmaku'

  id = Column(BIGINT, primary_key = True)
  mode = Column(TINYINT)
  font_size = Column(TINYINT)
  font_color = Column(INTEGER)
  send_time = Column(DATETIME)
  danmaku_pool = Column(TINYINT)
  danmaku_epoch = Column(DECIMAL(32, 5))
  user_hash = Column(BIGINT)
  user_id = Column(BIGINT)
  content = Column(String(1000))

  def __init__(self):
    self.id = -1
    self.mode = -1
    self.font_size = -1
    self.font_color = -1
    self.send_time = datetime.now()
    self.danmaku_pool = -1
    self.danmaku_epoch = -1.0
    self.user_hash = -1
    self.user_id = -1
    self.content = ''


@override_str
class AVCidsDO(Base):
  """
  av与cid的关系
  """
  __tablename__ = 'av_cids'

  cid = Column(BIGINT, primary_key = True)
  page = Column(INTEGER)
  pagename = Column(String(500))
  aid = Column(BIGINT)

  def __init__(self, aid: int, obj: AvDanmakuCid):
    self.cid = obj.cid
    self.page = obj.page
    self.pagename = obj.pagename
    self.aid = aid

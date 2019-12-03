from datetime import datetime, timezone, timedelta

from sqlalchemy import Column, BIGINT, DATETIME, String, INTEGER, PrimaryKeyConstraint
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

from online.AV import AV
from utils import override_str

Base = declarative_base()


@override_str
class AVInfoDO(Base):
  __tablename__ = 'av_info'
  __table_args__ = (
    PrimaryKeyConstraint('aid'),
  )

  test = -1
  aid = Column(BIGINT)
  videos = Column(INTEGER)
  tid = Column(INTEGER)
  tname = Column(String(255))
  copyright = Column(INTEGER)
  pic = Column(String(255))
  title = Column(String(500))
  pubdate = Column(DATETIME)
  ctime = Column(DATETIME)
  desc = Column(String(2000))
  state = Column(INTEGER)
  attribute = Column(INTEGER)
  duration = Column(INTEGER)
  mission_id = Column(BIGINT)
  dynamic = Column(String(2000))
  cid = Column(BIGINT)
  bvid = Column(String(255))
  owner_mid = Column(BIGINT)
  stat_aid = Column(BIGINT)
  right_bp = Column(TINYINT)
  right_elec = Column(TINYINT)
  right_download = Column(TINYINT)
  right_movie = Column(TINYINT)
  right_pay = Column(TINYINT)
  right_hd5 = Column(TINYINT)
  right_no_reprint = Column(TINYINT)
  right_autoplay = Column(TINYINT)
  right_ugc_pay = Column(TINYINT)
  right_is_cooperation = Column(TINYINT)
  right_ugc_pay_preview = Column(TINYINT)
  right_no_background = Column(TINYINT)
  dimension_width = Column(INTEGER)
  dimension_height = Column(INTEGER)
  dimension_rotate = Column(TINYINT)
  last_update_time = Column(DATETIME, onupdate = datetime.now(timezone(timedelta(hours = 8))))
  create_time = Column(DATETIME, default = datetime.now(timezone(timedelta(hours = 8))))

  def __init__(self, av: AV.OnlineList):
    self.aid = av.aid
    self.videos = av.videos
    self.tid = av.tid
    self.tname = av.tname
    self.copyright = av.copyright
    self.pic = av.pic
    self.title = av.title
    self.pubdate = datetime.fromtimestamp(av.pubdate, timezone(timedelta(hours = 8)))
    self.ctime = datetime.fromtimestamp(av.ctime, timezone(timedelta(hours = 8)))
    self.desc = av.desc
    self.state = av.state
    self.attribute = av.attribute
    self.duration = av.duration
    self.mission_id = av.mission_id if 'mission_id' in av.__dict__ is None else -1
    self.dynamic = av.dynamic
    self.cid = av.cid
    self.bvid = av.bvid
    self.owner_mid = av.owner.mid
    self.stat_aid = av.stat.aid
    self.right_bp = av.rights.bp
    self.right_elec = av.rights.elec
    self.right_download = av.rights.download
    self.right_movie = av.rights.movie
    self.right_pay = av.rights.pay
    self.right_hd5 = av.rights.hd5
    self.right_no_reprint = av.rights.no_reprint
    self.right_autoplay = av.rights.autoplay
    self.right_ugc_pay = av.rights.ugc_pay
    self.right_is_cooperation = av.rights.is_cooperation
    self.right_ugc_pay_preview = av.rights.ugc_pay_preview
    self.right_no_background = av.rights.no_background
    self.dimension_width = av.dimension.width
    self.dimension_height = av.dimension.height
    self.dimension_rotate = av.dimension.rotate
    self.last_update_time = datetime.now(timezone(timedelta(hours = 8)))

@override_str
class AVStatDO(Base):
  __tablename__ = 'av_stat'

  aid = Column(BIGINT, primary_key = True)
  create_time = Column(DATETIME, primary_key = True)
  view = Column(INTEGER)
  danmaku = Column(INTEGER)
  reply = Column(INTEGER)
  favorite = Column(INTEGER)
  coin = Column(INTEGER)
  share = Column(INTEGER)
  now_rank = Column(TINYINT)
  his_rank = Column(TINYINT)
  like = Column(INTEGER)
  dislike = Column(INTEGER)
  online_count = Column(INTEGER)

  def __init__(self, av: AV.OnlineList):
    self.aid = av.stat.aid
    self.create_time = datetime.now(timezone(timedelta(hours = 8)))
    self.view = av.stat.view
    self.danmaku = av.stat.danmaku
    self.reply = av.stat.reply
    self.favorite = av.stat.favorite
    self.coin = av.stat.coin
    self.share = av.stat.share
    self.now_rank = av.stat.now_rank
    self.his_rank = av.stat.his_rank
    self.like = av.stat.like
    self.dislike = av.stat.dislike
    self.online_count = av.online_count

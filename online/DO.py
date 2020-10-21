from datetime import datetime, timezone, timedelta

from selfusepy.utils import override_str
from sqlalchemy import Column, BIGINT, DATETIME, String, INTEGER, PrimaryKeyConstraint, BOOLEAN
from sqlalchemy.dialects.postgresql import SMALLINT

from config import Base
from online.Entity import AV


@override_str
class AVInfoDO(Base):
  """
  av详情
  """
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
  right_bp = Column(BOOLEAN)
  right_elec = Column(BOOLEAN)
  right_download = Column(BOOLEAN)
  right_movie = Column(BOOLEAN)
  right_pay = Column(BOOLEAN)
  right_hd5 = Column(BOOLEAN)
  right_no_reprint = Column(BOOLEAN)
  right_autoplay = Column(BOOLEAN)
  right_ugc_pay = Column(BOOLEAN)
  right_is_cooperation = Column(BOOLEAN)
  right_ugc_pay_preview = Column(BOOLEAN)
  right_no_background = Column(BOOLEAN)
  dimension_width = Column(INTEGER)
  dimension_height = Column(INTEGER)
  dimension_rotate = Column(BOOLEAN)
  last_update_time = Column(DATETIME, onupdate = datetime.now(timezone(timedelta(hours = 8))))
  create_time = Column(DATETIME, default = datetime.now(timezone(timedelta(hours = 8))))

  def __init__(self, av: AV.OnlineList = None):
    if av is None:
      return
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
    self.attribute = av.attribute if 'attribute' in av.__dict__ else -1
    self.duration = av.duration
    self.mission_id = av.mission_id if 'mission_id' in av.__dict__ else -1
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
  """
  av的状态详情, e.g. 投币, 点赞, 收藏
  """
  __tablename__ = 'av_stat'

  aid = Column(BIGINT, primary_key = True)
  create_time = Column(DATETIME, primary_key = True)
  view = Column(INTEGER)
  danmaku = Column(INTEGER)
  reply = Column(INTEGER)
  favorite = Column(INTEGER)
  coin = Column(INTEGER)
  share = Column(INTEGER)
  rank = Column(SMALLINT)
  now_rank = Column(SMALLINT)
  his_rank = Column(SMALLINT)
  like = Column(INTEGER)
  dislike = Column(INTEGER)
  online_count = Column(INTEGER)

  def __init__(self, av: AV.OnlineList, rank: int = 0, get_data_time: datetime = None):
    self.aid = av.stat.aid
    self.create_time = datetime.now(timezone(timedelta(hours = 8))) if get_data_time is None else get_data_time
    self.view = av.stat.view
    self.danmaku = av.stat.danmaku
    self.reply = av.stat.reply
    self.favorite = av.stat.favorite
    self.coin = av.stat.coin
    self.share = av.stat.share
    self.rank = rank
    self.now_rank = av.stat.now_rank
    self.his_rank = av.stat.his_rank
    self.like = av.stat.like
    self.dislike = av.stat.dislike
    self.online_count = av.online_count

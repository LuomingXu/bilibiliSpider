# encoding:utf-8

from typing import List

from selfusepy.jsonparse import BaseJsonObject
from selfusepy.utils import override_str


@override_str
class OnlineList(BaseJsonObject):
  """
  对应获取到的av数据的json格式的信息
  """

  def __init__(self):
    self.onlineList: List[OnlineList.AV] = [OnlineList.AV()]

  @override_str
  class AV(BaseJsonObject):

    def __init__(self):
      self.aid: int = -1
      self.videos: int = -1
      self.tid: int = -1
      self.tname: str = ""
      self.copyright: int = -1
      self.pic: str = ""
      self.title: str = ""
      self.pubdate: int = -1
      self.ctime: int = -1
      self.desc: str = ""
      self.state: int = -1
      self.attribute: int = -1
      self.duration: int = -1
      self.mission_id: int = -1
      self.rights: OnlineList.AV.Rights = OnlineList.AV.Rights()
      self.owner: OnlineList.AV.Owner = OnlineList.AV.Owner()
      self.stat: OnlineList.AV.Stat = OnlineList.AV.Stat()
      self.dynamic: str = ""
      self.cid: int = -1
      self.dimension: OnlineList.AV.Dimension = OnlineList.AV.Dimension()
      self.bvid: str = ""
      self.online_count: int = -1

    @override_str
    class Rights(BaseJsonObject):
      def __init__(self):
        self.bp: int = -1
        self.elec: int = -1
        self.download: int = -1
        self.movie: int = -1
        self.pay: int = -1
        self.hd5: int = -1
        self.no_reprint: int = -1
        self.autoplay: int = -1
        self.ugc_pay: int = -1
        self.is_cooperation: int = -1
        self.ugc_pay_preview: int = -1
        self.no_background: int = -1

    @override_str
    class Owner(BaseJsonObject):

      def __init__(self):
        self.mid: int = -1
        self.name: str = ""
        self.face: str = ""

    @override_str
    class Stat(BaseJsonObject):

      def __init__(self):
        self.aid: int = -1
        self.view: int = -1
        self.danmaku: int = -1
        self.reply: int = -1
        self.favorite: int = -1
        self.coin: int = -1
        self.share: int = -1
        self.now_rank: int = -1
        self.his_rank: int = -1
        self.like: int = -1
        self.dislike: int = -1

    @override_str
    class Dimension(BaseJsonObject):

      def __init__(self):
        self.width: int = -1
        self.height: int = -1
        self.rotate: int = -1

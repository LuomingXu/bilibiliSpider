from selfusepy.jsonparse import BaseJsonObject
from selfusepy.utils import override_str


@override_str
class AvDanmakuCid(BaseJsonObject):

  def __init__(self):
    self.page: int = -1
    self.pagename: str = ''
    self.cid: int = -1

from selfusepy.jsonparse import BaseJsonObject
from selfusepy.utils import override_str


@override_str
class AvDanmakuCid(BaseJsonObject):

  def __init__(self):
    self.page: int = -1
    self.pagename: str = ''
    self.cid: int = -1


@override_str
class CustomTag(object):

  def __init__(self, content, tag_content):
    self.content: str = content
    self.tag_content: str = tag_content

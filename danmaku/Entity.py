from selfusepy.jsonparse import BaseJsonObject
from selfusepy.utils import override_str


@override_str
class AvDanmakuCid(BaseJsonObject):
  """
  av对应的cid详情
  """

  def __init__(self):
    self.page: int = -1
    self.pagename: str = ''
    self.cid: int = -1


@override_str
class CustomTag(object):
  """
  由于bs4的Tag无法多进程传参, 进行了自定义的Tag封装
  """

  def __init__(self, content, tag_content, aid = None, cid = None):
    self.content: str = content
    self.tag_content: str = tag_content
    self.aid: int = aid
    self.cid: int = cid

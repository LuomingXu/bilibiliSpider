from datetime import datetime
from enum import Enum

from selfusepy.utils import override_str

__all__ = ['CustomFile', 'FileType']


class FileType(Enum):
  Online = 0
  Danmaku = 1
  AvCids = 2


@override_str
class CustomFile(object):
  def __init__(self, file_name: str, content: str, file_type: FileType, create_time: datetime = None,
               aid: int = None, cid: int = None):
    self.file_name: str = file_name
    self.file_type: FileType = file_type
    self.content: str = content
    self.create_time: datetime = create_time
    self.aid: int = aid
    self.cid: int = cid

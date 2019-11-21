# encoding:utf-8
from utils import override_str


@override_str
class Data(object):

  def __init__(self):
    self.mid: str = ''
    self.name: str = ''
    self.sex: str = ''
    self.face: str = ''
    self.sign: str = ''
    self.rank: int = -1
    self.level: int = -1
    self.jointime: int = -1
    self.moral: int = -1
    self.silence: int = -1
    self.birthday: str = ''
    self.coins: int = -1
    self.fans_badge: bool = None
    self.official: Data.Official = None
    self.vip: Data.Vip = None
    self.is_followed: bool = None
    self.top_photo: str = ''
    self.theme: str = ''
    self.sys_notice: str = ''

  class Official(object):

    def __init__(self):
      self.role: int = -1
      self.title: str = ''
      self.desc: str = ''

  class Vip(object):

    def __init__(self):
      self.type: int = -1
      self.status: int = -1
      self.theme_type: int = -1

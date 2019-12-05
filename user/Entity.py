from selfusepy.utils import override_str


@override_str
class UserProfile(object):

  @classmethod
  def from_dict(clazz, dict):
    obj = clazz()
    obj.__dict__.update(dict)
    return obj

  def __init__(self):
    self.code: int = -1
    self.message: str = ''
    self.ttl: int = -1
    self.data: UserProfile.Data = None

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
      self.official: UserProfile.Data.Official = None
      self.vip: UserProfile.Data.Vip = None
      self.is_followed: bool = None
      self.top_photo: str = ''
      self.theme: str = ''
      self.sys_notice: str = ''

    class Official(object):

      def __init__(self):
        self.role: int = -1
        self.title: str = ''
        self.desc: str = ''
        self.type: int = -1

    class Vip(object):

      def __init__(self):
        self.type: int = -1
        self.status: int = -1
        self.theme_type: int = -1

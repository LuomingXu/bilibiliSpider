from selfusepy.utils import override_str
from selfusepy.jsonparse import BaseJsonObject


@override_str
class UserProfile(BaseJsonObject):
  """
  对应获取到的用户信息的json
  """

  # @classmethod
  # def from_dict(clazz, dict):
  #   obj = clazz()
  #   obj.__dict__.update(dict)
  #   return obj

  def __init__(self):
    self.code: int = -1
    self.message: str = ''
    self.ttl: int = -1
    self.data: UserProfile.Data = UserProfile.Data()

  @override_str
  class Data(BaseJsonObject):

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
      self.fans_badge: bool = False
      self.official: UserProfile.Data.Official = UserProfile.Data.Official()
      self.vip: UserProfile.Data.Vip = UserProfile.Data.Vip()
      self.is_followed: bool = False
      self.top_photo: str = ''
      self.theme: UserProfile.Data.Theme = UserProfile.Data.Theme()
      self.sys_notice: UserProfile.Data.Sys_notice = UserProfile.Data.Sys_notice()

    @override_str
    class Official(BaseJsonObject):

      def __init__(self):
        self.role: int = -1
        self.title: str = ''
        self.desc: str = ''
        self.type: int = -1

    @override_str
    class Vip(BaseJsonObject):

      def __init__(self):
        self.type: int = -1
        self.status: int = -1
        self.theme_type: int = -1

    @override_str
    class Theme(BaseJsonObject):
      pass

    @override_str
    class Sys_notice(BaseJsonObject):
      pass

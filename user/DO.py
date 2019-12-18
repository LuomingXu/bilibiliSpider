from sqlalchemy import Column, String, BIGINT, INT, DECIMAL
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

from user.Entity import UserProfile
from selfusepy.utils import override_str

Base = declarative_base()


@override_str
class UserProfileDO(Base):
  """
  用户
  """
  __tablename__ = 'bilibili'

  # table structure
  mid = Column(BIGINT, primary_key = True)
  name = Column(String(500))
  face = Column(String(1000))
  rank = Column(INT)
  level = Column(INT)
  birthday = Column(String(50))
  sign = Column(String(500))
  fans_badge = Column(TINYINT)
  vip_type = Column(INT)
  vip_status = Column(INT)
  official_title = Column(String(100))
  official_type = Column(TINYINT)
  official_role = Column(TINYINT)

  def __init__(self, userProfile: UserProfile):
    self.mid = userProfile.data.mid
    self.name = userProfile.data.name
    self.face = userProfile.data.face
    self.rank = userProfile.data.rank
    self.level = userProfile.data.level
    self.birthday = userProfile.data.birthday
    self.sign = userProfile.data.sign
    self.fans_badge = userProfile.data.fans_badge
    self.vip_type = userProfile.data.vip.type
    self.vip_status = userProfile.data.vip.status
    self.official_title = userProfile.data.official.title
    self.official_type = userProfile.data.official.type
    self.official_role = userProfile.data.official.role

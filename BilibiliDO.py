# encoding:utf-8

from sqlalchemy import Column, String, BIGINT, INT, DECIMAL
from sqlalchemy.ext.declarative import declarative_base

from Bilibili import UserProfile
from utils import override_str

Base = declarative_base()


@override_str
class UserProfileDO(Base):
  __tablename__ = 'bilibili'

  # table structure
  mid = Column(BIGINT, primary_key = True)
  name = Column(String(500))
  face = Column(String(1000))
  rank = Column(INT)
  level = Column(INT)
  birthday = Column(String(50))
  coins = Column(DECIMAL(32, 2))
  vip_type = Column(INT)
  vip_status = Column(INT)

  def __init__(self, userProfile: UserProfile):
    self.mid = userProfile.data.mid
    self.name = userProfile.data.name
    self.face = userProfile.data.face
    self.rank = userProfile.data.rank
    self.level = userProfile.data.level
    self.birthday = userProfile.data.birthday
    self.coins = userProfile.data.coins
    self.vip_type = userProfile.data.vip.type
    self.vip_status = userProfile.data.vip.status

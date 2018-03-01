from sqlalchemy import ForeignKey, Column, Integer, String, TIMESTAMP
from .database import Base


class TGUser(Base):
    __tablename__ = 'tg_users'

    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer)
    tg_username = Column(String(50))

    def __repr__(self):
        return self.tg_username


class VKUser(Base):
    __tablename__ = 'vk_users'

    id = Column(Integer, primary_key=True)
    vk_user_id = Column(Integer)
    vk_username = Column(String(50))

    def __repr__(self):
        return self.vk_username


class TGChannel(Base):
    __tablename__ = 'tg_channels'

    id = Column(Integer, primary_key=True)
    tg_channel_id = Column(Integer)
    tg_channel_name = Column(String(50))

    def __repr__(self):
        return self.tg_channel_name

class VKGroup(Base):
    __tablename__ = 'vk_groups'

    id = Column(Integer, primary_key=True)
    vk_group_id = Column(Integer)

    def __repr__(self):
        return self.vk_group_id

class TGPost(Base):
    __tablename__ = 'tg_posts'

    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP)
    channel_id = Column(Integer, ForeignKey('tg_users.id'))

    #TODO Сделать relationship

    def __repr__(self):
        return '{} {}'.format(self.timestamp, self.channel_id)

from sqlalchemy import ForeignKey, Column, Integer, String, TIMESTAMP, BIGINT
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class TGUser(Base):
    """
    Класс определяет пользователя телеграма (id и username).
    Связан с таблицей каналов.
    """
    __tablename__ = 'tg_users'

    id = Column(Integer, primary_key=True)
    tg_user_id = Column(BIGINT, nullable=False, unique=True)
    tg_username = Column(String(50))


class VKUser(Base):
    """
    Класс определяет пользователя вконтакте (id и username)
    Связан с таблицей групп.
    """
    __tablename__ = 'vk_users'

    id = Column(Integer, primary_key=True)
    vk_user_id = Column(BIGINT, nullable=False)
    vk_username = Column(String(50))


class TGChannel(Base):
    __tablename__ = 'tg_channels'

    id = Column(Integer, primary_key=True)
    tg_channel_id = Column(BIGINT, nullable=False)
    tg_channel_name = Column(String(50))

    # Связь канал<->пользователь
    tg_user_id = Column(Integer, ForeignKey('tg_users.id'), nullable=False)
    tg_user = relationship('TGUser', backref='channels')

    # Связь канал<->группаВК
    vk_group_id = Column(Integer, ForeignKey('vk_groups.id'))
    vk_group = relationship('VKGroup', backref='channels')


class VKGroup(Base):
    __tablename__ = 'vk_groups'

    id = Column(Integer, primary_key=True)
    vk_group_id = Column(BIGINT, nullable=False)

    # Связь группа<->пользователь
    vk_user_id = Column(Integer, ForeignKey('vk_users.id'), nullable=False)
    vk_user = relationship('VKUser', backref='groups')


class TGPost(Base):
    __tablename__ = 'tg_posts'

    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, default=datetime.now, nullable=False)

    # Связь пост<->канал
    tg_channel_id = Column(Integer, ForeignKey('tg_channels.id'), nullable=False)
    tg_channel = relationship('TGChannel', backref='posts')


from sqlalchemy import ForeignKey, Column, Integer, String, TIMESTAMP, BIGINT, Enum
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import enum


class PaidEnum(enum.Enum):
    paid = 1  # Если канал оплачен
    not_paid = 0  # Если канал не оплачен


class TGUser(Base):
    """
    Класс определяет пользователя телеграма (id и username).
    Связан с таблицей каналов.
    """
    __tablename__ = 'tg_users'

    id = Column(Integer, primary_key=True)
    tg_user_id = Column(BIGINT, nullable=False, unique=True)
    tg_first_name = Column(String(50), nullable=False)
    dialog_state = Column(String(50))

    def get_tg_first_name(self):
        # Returns telegram first name of user
        return self.tg_first_name

    def get_dialog_state(self):
        # Returns state of dialog with user
        return self.dialog_state


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

    # Оплачено ли использование бота для данного канала
    paid = Column(Enum(PaidEnum), default=PaidEnum.not_paid)

    def is_paid(self):
        if self.paid:
            return True
        else:
            return False


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


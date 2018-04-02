from sqlalchemy import ForeignKey, Column, Integer, String, TIMESTAMP, BIGINT
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class PaidEnum:
    PAID = 1  # Если оплачено
    NOT_PAID = 0  # Если не оплачено


class ChannelStateEnum:
    ON = 1  # Если канал включен
    OFF = 0  # Если канал выключен


class TGUser(Base):
    """
    Класс определяет пользователя телеграма (id и username).
    Связан с таблицей каналов.
    """
    __tablename__ = 'tg_users'

    id = Column(Integer, primary_key=True)
    tg_user_id = Column(BIGINT, nullable=False, unique=True)
    tg_first_name = Column(String(50, convert_unicode=True), nullable=False)
    dialog_state = Column(String(50, convert_unicode=True), default="")
    tg_channels = relationship("TGChannel", back_populates="tg_user", cascade="all, delete, delete-orphan")
    # Оплачено ли использование бота для данного пользователя
    paid = Column(Integer, default=PaidEnum.NOT_PAID)

    def is_paid(self):
        if self.paid:
            return True
        else:
            return False

    def get_tg_first_name(self):
        # Returns telegram first name of user
        return self.tg_first_name

    def get_dialog_state(self):
        # Returns state of dialog with user
        return self.dialog_state

    def __repr__(self):
        return "<TGUser entity {tg_user_id: %d, tg_first_name: %s, dialog_state: %s}>" % \
               (self.tg_user_id, self.tg_first_name, self.dialog_state)


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
    vk_group = relationship('VKGroup', backref='tg_channel')

    # Триггер вкл/выкл
    state = Column(Integer, default=ChannelStateEnum.OFF)

    posts = relationship("TGPost", back_populates="tg_channel", cascade="all, delete, delete-orphan")

    def get_channel_state(self):
        return self.state

    def get_channel_name(self):
        return self.tg_channel_name


class VKGroup(Base):
    __tablename__ = 'vk_groups'

    id = Column(Integer, primary_key=True)
    vk_group_id = Column(BIGINT, nullable=False)
    vk_token = Column(String(100, convert_unicode=True), nullable=False)

    def __repr__(self):
        return "<type: VK group, vk_group_id: {}>".format(self.vk_group_id)


class TGPost(Base):
    __tablename__ = 'tg_posts'

    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, default=datetime.now, nullable=False)

    # Связь пост<->канал
    tg_channel_id = Column(Integer, ForeignKey('tg_channels.id'), nullable=False)
    tg_channel = relationship('TGChannel', back_populates='posts')


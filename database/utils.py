from database.models import *
from sqlalchemy.exc import *


def add_tg_user(session, tg_user_id, tg_first_name):
    """
    Adds telegram user in database
    :param session: session object
    :param tg_user_id: Telegram user ID, integer
    :param tg_first_name: First name of user, string
    :return: TGUser class entity
    """
    tg_user = TGUser(tg_user_id=tg_user_id,
                     tg_first_name=tg_first_name)
    session.add(tg_user)
    session.commit()
    return tg_user


def add_vk_user(session, vk_user_id):
    """
    Adds vkontakte user in database
    :param session: session object
    :param vk_user_id: VK user id, integer
    :return: VKUser class entity
    """
    vk_user = VKUser(vk_user_id=vk_user_id)
    session.add(vk_user)
    session.commit()
    return vk_user


def add_tg_channel(session, tg_channel_id, tg_user):
    """
    Adds telegram channel to database
    :param session: session object
    :param tg_channel_id: Telegram channel id, integer
    :param tg_user: TGUser class entity
    :return: TGChannel class entity
    """
    tg_channel = TGChannel(tg_channel_id=tg_channel_id,
                           tg_user=tg_user)
    session.add(tg_channel)
    session.commit()
    return tg_channel


def add_vk_group(session, vk_group_id, vk_user):
    """
    Adds new vkontakte group
    :param session: session object
    :param vk_group_id: VK group id, integer
    :param vk_user: VKUser class entity
    :return: VKGroup class entity
    """
    vk_group = VKGroup(vk_group_id=vk_group_id,
                       vk_user=vk_user)
    session.add(vk_group)
    session.commit()
    return vk_group


def add_tg_post(session, tg_channel):
    """
    Adds new telegram post record. Automatically adds timestamp, when crates
    :param session: session object
    :param tg_channel: TGChannel class entity
    :return: TGPost class entity
    """
    tg_post = TGPost(tg_channel=tg_channel)
    session.add(tg_post)
    session.commit()
    return tg_post


def bind_channel_with_group(session, tg_channel, vk_group):
    """
    Bind telegram channel with VK group
    :param session: session object
    :param tg_channel: TGChannel class entity
    :param vk_group: VKGroup class entity
    :return:
    """
    tg_channel.vk_group = vk_group
    session.add(tg_channel)
    session.commit()


def get_channels(session, tg_user):
    """
    Get list of channels by tg_user
    :param session: session object
    :param tg_user: TGUser class entity
    :return: list of TGChannel objects
    """
    return session.query(TGChannel).filter_by(tg_user_id=tg_user.id).all()


def get_posts_by_channel(session, tg_channel):
    """
    Get list of TG posts by telegram channel
    :param session: session object
    :param tg_channel: TGChannel class entity
    :return: list of TGPost objects
    """
    return session.query(TGPost).filter_by(tg_channel_id=tg_channel.id).all()


def get_tg_user(session, tg_user_id):
    """
    Get telegram user object by tg_user_id
    :param session: session object
    :param tg_user_id: ID of user in telegram, integer
    :return: TGUser class entity
    """
    return session.query(TGUser).filter_by(tg_user_id=tg_user_id).first()

from database.models import *
from .models import PaidEnum, ChannelStateEnum


'''
session.query().all() - возвращает результат запроса в виде списка
session.query().count() - возвращает количество строк в результате запроса
session.query().delete() - удаляет записи (http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.delete)
session.query().filter() - применяет фильтр с использованием SQL выражений
session.query().filter_by() - применяет фильтр с использованием выражений с ключевыми словами
session.query().first() - возвращает первый результат
session.query().get(primary_key_value) - возвращает результат на основе primary key
session.query().join() - http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.join
'''


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


def add_tg_channel(session, tg_channel_id, tg_user_id, tg_channel_name=""):
    """
    Adds telegram channel to database
    :param session: session object
    :param tg_channel_id: Telegram channel id, integer
    :param tg_user_id: TGUser class entity
    :param tg_channel_name: Name of channel, String
    :return: TGChannel class entity
    """
    tg_channel = TGChannel(tg_channel_id=tg_channel_id,
                           tg_user=get_tg_user(session, tg_user_id),
                           tg_channel_name=tg_channel_name)
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


def add_tg_post(session, tg_channel_id):
    """
    Adds new telegram post record. Automatically adds timestamp, when crates
    :param session: session object
    :param tg_channel_id: TG Channel id, integer
    :return: TGPost class entity
    """
    tg_channel = get_channel_by_id(session, tg_channel_id)
    tg_post = TGPost(tg_channel=tg_channel)
    session.add(tg_post)
    session.commit()
    return tg_post


def bind_channel_with_group(session, tg_channel_id, vk_group):
    """
    Bind telegram channel with VK group
    :param session: session object
    :param tg_channel_id: TG Channel id, integer
    :param vk_group: VKGroup class entity
    :return: None
    """
    tg_channel = get_channel_by_id(session, tg_channel_id)
    tg_channel.vk_group = vk_group
    session.add(tg_channel)
    session.commit()


def get_channels(session, tg_user_id=None):
    """
    Get list of channels by tg_user
    :param session: session object
    :param tg_user_id: TG user id or None if need all channels in DB
    :return: list of TG Channel ids
    """
    if not tg_user_id:
        channels = session.query(TGChannel).all()
    else:
        tg_user = get_tg_user(session, tg_user_id)
        channels = session.query(TGChannel).filter_by(tg_user_id=tg_user.id).all()
    return [channel.tg_channel_id for channel in channels]


def get_posts_by_channel(session, tg_channel_id=None):
    """
    Get list of TG posts by telegram channel
    :param session: session object
    :param tg_channel_id: TG Channel id, integer
    :return: list of TGPost objects
    """
    if tg_channel_id:
        return session.query(TGPost).filter_by(tg_channel_id=get_channel_by_id(session, tg_channel_id).id).all()
    else:
        return session.query(TGPost).all()


def get_tg_user(session, tg_user_id):
    """
    Get telegram user object by tg_user_id
    :param session: session object
    :param tg_user_id: ID of user in telegram, integer
    :return: TGUser class entity
    """
    return session.query(TGUser).filter_by(tg_user_id=tg_user_id).first()


def get_channel_by_id(session, tg_channel_id):
    """
    Get TGChannel class entity
    :param session:  session object
    :param tg_channel_id: telegram channel id, integer
    :return: TGChannel class entity
    """
    return session.query(TGChannel).filter_by(tg_channel_id=tg_channel_id).first()


def set_channel_name(session, tg_channel_id, channel_name):
    """
    Set TG channel name
    :param session: session object
    :param tg_channel_id: telegram channel id, integer
    :param channel_name: channel name, string
    :return: None
    """
    channel = get_channel_by_id(session, tg_channel_id)
    channel.tg_channel_name = channel_name
    session.add(channel)
    session.commit()


def update_user_dialog_state(session, tg_user_id, state):
    """
    Update dialog state with user
    :param session: session object
    :param tg_user_id: ID of user in telegram, integer
    :param state: dialog state, String (max 50)
    :return: None
    """
    tg_user = get_tg_user(session, tg_user_id)
    tg_user.dialog_state = state
    session.add(tg_user)
    session.commit()


def is_channel_on(session, tg_channel_id):
    """
    Returns True if state of channel == ON, False if OFF
    :param session: session object
    :param tg_channel_id: telegram channel id, integer
    :return: bool
    """
    channel = get_channel_by_id(session, tg_channel_id)
    if channel.get_channel_state():
        return True
    else:
        return False


def set_channel_on(session, tg_channel_id):
    """
    Changes state of channel to ON
    :param session: session object
    :param tg_channel_id: telegram channel id, integer
    :return: None
    """
    channel = get_channel_by_id(session, tg_channel_id)
    channel.state = ChannelStateEnum.ON
    session.add(channel)
    session.commit()


def set_channel_off(session, tg_channel_id):
    """
    Changes state of channel to OFF
    :param session: session object
    :param tg_channel_id: telegram channel id, integer
    :return: None
    """
    channel = get_channel_by_id(session, tg_channel_id)
    channel.state = ChannelStateEnum.OFF
    session.add(channel)
    session.commit()


def is_user_paid(session, tg_user_id):
    """
    Returns True if user paid, False otherwise
    :param session: session object
    :param tg_user_id: ID of user in telegram, integer
    :return: bool
    """
    tg_user = get_tg_user(session, tg_user_id)
    return tg_user.is_paid()


def set_user_paid(session, tg_user_id):
    """
    Changes payment state for user to PAID
    :param session: session object
    :param tg_user_id: ID of user in telegram, integer
    :return: None
    """
    tg_user = get_tg_user(session, tg_user_id)
    if tg_user.is_paid():
        pass
    else:
        tg_user.paid = PaidEnum.PAID
        session.add(tg_user)
        session.commit()


def set_user_not_paid(session, tg_user_id):
    """
    Changes payment state for user to NOT_PAID
    :param session: session object
    :param tg_user_id: ID of user in telegram, integer
    :return: None
    """
    tg_user = get_tg_user(session, tg_user_id)
    if not tg_user.is_paid():
        pass
    else:
        tg_user.paid = PaidEnum.NOT_PAID
        session.add(tg_user)
        session.commit()


def delete_channel(session, tg_channel_id):
    """
    Delete channel and related posts and vk group
    :param session: session object
    :param tg_channel_id: channel id, integer
    :return: None
    """
    channel = get_channel_by_id(session, tg_channel_id)
    if not channel:
        pass
    else:
        vk_group = session.query(VKGroup).get(channel.vk_group_id)
        session.delete(channel)
        if vk_group:
            session.delete(vk_group)
        session.commit()


def delete_tg_user(session, tg_user_id):
    """
    Delete telegram user with related channels
    :param session: session object
    :param tg_user_id: telegram user id, integer
    :return: None
    """
    tg_user = get_tg_user(session, tg_user_id)
    if not tg_user:
        pass
    else:
        session.delete(tg_user)
        session.commit()


def get_num_posts(session, tg_channel_id):
    """
    Get number of posts for given channel
    :param session: session object
    :param tg_channel_id: telegram channel id, integer
    :return: None
    """
    tg_channel = get_channel_by_id(session, tg_channel_id)
    if tg_channel:
        return session.query(TGPost).filter_by(tg_channel_id=tg_channel.id).count()
    else:
        pass

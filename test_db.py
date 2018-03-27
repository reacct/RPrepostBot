from database.models import *
from database.database import engine, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database, drop_database
from database import utils

# пересоздаём базу перед тестами
if database_exists(engine.url):
    try:
        drop_database(engine.url)
    except:
        print('Problems with database drop')
    try:
        create_database(engine.url, encoding='utf8mb4')
    except:
        print('Problem with database creation')


# создаём все таблицы заново перед тестами
Base.metadata.create_all(engine)
# создаём сессию для работы с базой
Session = sessionmaker(bind=engine)
session = Session()

# создаём тестовых пользователей
test_tg_user = utils.add_tg_user(session, 6123456, "test_user")
test_vk_user = utils.add_vk_user(session, 6789012)
test_vk_group = utils.add_vk_group(session, -4567890, test_vk_user)
test_tg_channel = utils.add_tg_channel(session, -4022001, test_tg_user)
test_tg_channel = utils.add_tg_channel(session, -4022005, test_tg_user)

test_tg_post = utils.add_tg_post(session, test_tg_channel)
test_tg_post_1 = utils.add_tg_post(session, test_tg_channel)

utils.update_user_dialog_state(session, 6123456, "hello")

test_tg_user_2 = utils.add_tg_user(session, 54687944, "test_user_2")
test_tg_channel = utils.add_tg_channel(session, -5468798, test_tg_user_2)


print(utils.get_channels(session))

print(utils.get_channels(session, 6123456))

print(utils.get_tg_user(session, 6123456).get_dialog_state())

print(utils.get_tg_user(session, 6123456).get_tg_first_name())

print(utils.get_tg_user(session, 54687944))

# задать имя каналу
utils.set_channel_name(session, -4022005, "Abracadabra")

# получить имя канала
print(utils.get_channel_by_id(session, -4022005).get_channel_name())

# Проверяем состояние оплаты и состояние канала (вкл/выкл)
print(utils.is_user_paid(session, 6123456))
print(utils.is_channel_on(session, -4022005))

# Меняем состояние канала и состояние оплаты
utils.set_channel_on(session, -4022005)
print(utils.is_channel_on(session, -4022005))

utils.set_user_paid(session, 6123456)
print(utils.is_user_paid(session, 6123456))

session.close()

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
        create_database(engine.url, encoding='utf8')
    except:
        print('Problem with database creation')


# создаём все таблицы заново перед тестами
Base.metadata.create_all(engine)
# создаём сессию для работы с базой
Session = sessionmaker(bind=engine)
session = Session()

# создаём тестовых пользователей
test_tg_user = utils.add_tg_user(session, 6123456, "asdf")
test_tg_channel = utils.add_tg_channel(session, -4022001, 6123456)
test_tg_channel_2 = utils.add_tg_channel(session, -4022005, 6123456)

test_tg_post = utils.add_tg_post(session, -4022001)
test_tg_post_1 = utils.add_tg_post(session, -4022001)

for i in range(5):
    utils.add_tg_post(session, -4022005)

utils.update_user_dialog_state(session, 6123456, "привет")

test_tg_user_2 = utils.add_tg_user(session, 54687944, "test_user_2")
test_tg_channel_3 = utils.add_tg_channel(session, -5468798, 54687944)


print(utils.get_channels(session))

print(utils.get_channels(session, 6123456))

print(utils.get_tg_user(session, 6123456).get_dialog_state())

print(utils.get_tg_user(session, 6123456).get_tg_first_name())

print(utils.get_tg_user(session, 54687944))

utils.bind_channel_with_group(session, -4022001, utils.add_vk_group(session, -43523541, "ddfqad12312qwdqdwrg"))

# задать имя каналу
utils.set_channel_name(session, -4022005, "Имя на русском языке!")

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

# Получаем tg_user_id по tg_channel_id
print("Получаем tg_user_id по tg_channel_id -4022005")
print(utils.get_tg_user_id(session, -4022005))

# Получаем вк токен по vk_group_id
print("Получаем вк токен по vk_group_id -43523541")
print(utils.get_vk_token(session, -43523541))

# Количество постов для канала
print("В канале с id {} {} постов".format(test_tg_channel.tg_channel_id,
                                          utils.get_num_posts(session, test_tg_channel.tg_channel_id)))

print(test_tg_channel.posts)

# Удаляем канал
utils.delete_channel(session, -4022001)

print("В канале с id {} {} постов".format(-4022001,
                                          utils.get_num_posts(session, -4022001)))

print(utils.get_posts_by_channel(session))

print(utils.get_posts_by_channel(session, -4022005))

# Удаляем пользователя
utils.delete_tg_user(session, 6123456)

print(utils.get_posts_by_channel(session))


session.close()

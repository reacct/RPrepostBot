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
test_tg_user = utils.add_tg_user(session, -6123456, "test_user")
test_vk_user = utils.add_vk_user(session, -6789012)
tes_vk_group = utils.add_vk_group(session, -4567890, test_vk_user)
test_tg_channel = utils.add_tg_channel(session, -4022001, test_tg_user)
test_tg_channel = utils.add_tg_channel(session, -4022005, test_tg_user)

test_tg_post = utils.add_tg_post(session, test_tg_channel)
test_tg_post_1 = utils.add_tg_post(session, test_tg_channel)

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

print(utils.get_tg_user(session, 12345))

session.close()

from database.models import User
from database.database import engine, Base
from sqlalchemy.orm import sessionmaker

# очищаем все таблицы перед тестами
Base.metadata.drop_all(engine)
# создаём все таблицы заново перед тестами
Base.metadata.create_all(engine)
# создаём сессию для работы с базой
Session = sessionmaker(bind=engine)
session = Session()

# создаём тестовых пользователей
test_users = ['pig', 'dog', 'cat', 'bird']

session.add_all([User(tg_username=user) for user in test_users])
session.commit()

for instance in session.query(User):
    print(instance)

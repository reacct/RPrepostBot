from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from .config import *


# Возможно использование драйвера pymysql: mysql+pymysql
engine = create_engine('mysql://{}:{}@{}/{}?charset=utf8'.format(USER, PASSWORD, SERVER, DATABASE),
                       encoding='utf8',
                       convert_unicode=True)
Base = declarative_base()

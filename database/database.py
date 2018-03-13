from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from .config import *


# Возможно использование драйвера pymysql: mysql+pymysql
engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(USER, PASSWORD, SERVER, DATABASE))
Base = declarative_base()

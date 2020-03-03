from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

#Define User data model.
class User(Base):
    __tablename__='users'
    id = Column(Integer, primary_key=True)

    #User authentication fields.
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False, unique=True)

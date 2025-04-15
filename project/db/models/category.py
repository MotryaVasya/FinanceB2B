from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Numeric, ForeignKey, create_engine

from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_engine('sqlite:///finanse.db')

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    firstname = Column(String, nullable=False)
    secondname= Column(String, nullable=True)
    tg_id= Column(Integer, nullable=False)
    cash = Column(Numeric, nullable=False)

    # TODO спросить по поводу numeric нам нужен float в пайтоне

class Category(Base):
    __tablename__ = 'category'

    id= Column(Integer, primary_key=True)
    nameCategory= Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)

    user= relationship('User', backref='categories')


class Transaction(Base):
    __tablename__ = 'transaction'

    id= Column(Integer, primary_key=True)
    fullSum = Column(Numeric, nullable=False)
    date = Column(DateTime, default=datetime.now)
    description = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'))  
    user_id = Column(Integer, ForeignKey('user.id'))

   
    category = relationship('Category', backref='transactions')
    user = relationship('User', backref='transactions')


Base.metadata.create_all(engine)
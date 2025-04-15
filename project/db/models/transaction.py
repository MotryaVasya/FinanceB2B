# from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
# from base import Base
# import datetime 
# from sqlalchemy.orm import relationship

# class Transaction(Base):
#     __tablename__ = 'transaction'

#     id= Column(Integer, primary_key=True)
#     fullSum = Column(Numeric, nullable=False)
#     date = Column(DateTime, default=datetime.now)
#     description = Column(String, nullable=False)
#     category_id = Column(Integer, ForeignKey('category.id'))  
#     user_id = Column(Integer, ForeignKey('user.id'))

   
#     category = relationship('Category', backref='transactions')
#     user = relationship('User', backref='transactions')

#     # TODO спросить по поводу numeric нам нужен float в пайтоне
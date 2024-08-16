from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Feed(Base):
    __tablename__ = 'feed'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    type = Column(String)
    pet = Column(String)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    address = Column(String)
    time = Column(Integer)
    # Зв'язок багато-до-багатьох з товарами
    feeds = relationship('Feed', secondary='order_feed', backref='orders')

class OrderFeed(Base):
    __tablename__ = 'order_feed'
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    feed_id = Column(Integer, ForeignKey('feed.id'), primary_key=True)


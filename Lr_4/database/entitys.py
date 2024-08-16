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

def to_dict(obj, seen=None):
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return None  # Skip cyclic reference
    seen.add(obj_id)

    data = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    for rel in obj.__mapper__.relationships:
        value = getattr(obj, rel.key)
        if value is None:
            data[rel.key] = None
        elif isinstance(value, list):
            data[rel.key] = [to_dict(item, seen) for item in value]
        else:
            data[rel.key] = to_dict(value, seen)
    return data

from engine import engine
from entitys import Base


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    print('Database created.')
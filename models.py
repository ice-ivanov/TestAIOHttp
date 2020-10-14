from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

DB_URI = 'sqlite:///sqlite.db'
Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI))
session = scoped_session(Session)
Base = declarative_base()


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    surname = Column(String(50))
    sex = Column(String(50))

    def __init__(self, name, surname, sex):
        self.name = name
        self.surname = surname
        self.sex = sex

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_json(self):
        to_serialize = ['id', 'name', 'surname', 'sex']
        d = {}
        for attr_name in to_serialize:
            d[attr_name] = getattr(self, attr_name)
        return d


class Car(Base):
    __tablename__ = 'car'
    id = Column(Integer, primary_key=True)
    model = Column(String(50))
    year = Column(String(50))

    def __init__(self, model, year):
        self.model = model
        self.year = year

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_json(self):
        to_serialize = ['id', 'model', 'year']
        d = {}
        for attr_name in to_serialize:
            d[attr_name] = getattr(self, attr_name)
        return d


class Part(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    model = Column(String(50))
    country = Column(String(50))

    def __init__(self, name, model, country):
        self.name = name
        self.model = model
        self.country = country

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_json(self):
        to_serialize = ['id', 'name', 'model', 'country']
        d = {}
        for attr_name in to_serialize:
            d[attr_name] = getattr(self, attr_name)
        return d


# creates database
if __name__ == "__main__":
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

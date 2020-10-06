from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import BigInteger, String, Boolean, DateTime, Integer, Text, Float
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, joinedload
from sqlalchemy.ext.declarative import declarative_base

# Create a (lazy) database engine
engine = create_engine('sqlite:///db.sqlite')

# Create a base class to define all the database subclasses
TableDeclarativeBase = declarative_base(bind=engine)

# Create a Session class able to initialize database sessions
session = scoped_session(sessionmaker())


class Description(TableDeclarativeBase):
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    __tablename__ = "description"

    def __str__(self):
        return f"{self.text[:10]}"

    def __repr__(self):
        return f"<ProductCategory {self.id}>"


TableDeclarativeBase.metadata.create_all()

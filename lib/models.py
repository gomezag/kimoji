from sqlalchemy import Boolean, Column, Integer, String

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True)
    state = Column(String)

from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from kimoji.lib.db import Base


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


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    machine = relationship("Machine")
    loss = Column(Float, default=-1)
    name = Column(String, unique=True)
    state = Column(String)

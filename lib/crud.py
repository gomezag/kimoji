from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import models, schemas


def get_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user:
        return user


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, hashed_password=user.hashed_password, username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user: schemas.User):
    db_user = get_user(db, user.username)
    db.delete(db_user)
    db.commit()


def get_machine(db: Session, name: str) -> models.Machine:
    machine = db.query(models.Machine).filter(models.Machine.name == name).first()
    if machine:
        return machine


def get_machines(db: Session) -> List[models.Machine]:
    machines = db.query(models.Machine).all()
    if machines:
        return machines
    else:
        return []


def create_machine(db: Session, machine: schemas.MachineCreate) -> models.Machine:
    machine = models.Machine(**machine.model_dump())
    machine.state = 'CREATED'
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


def get_or_create_machine(db: Session, machine: schemas.MachineCreate) -> models.Machine:
    try:
        machine = create_machine(db, machine)
    except IntegrityError:
        db.rollback()
        machine = get_machine(db, machine.name)

    return machine


def delete_machine(db: Session, machine_name: str) -> None:
    machine = get_machine(db, machine_name)
    db.delete(machine)
    db.commit()

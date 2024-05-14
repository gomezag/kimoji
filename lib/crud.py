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


def get_simulation_run(db: Session, value: str or int, key: str = 'name'):
    attribute = getattr(models.SimulationRun, key, None)
    if attribute:
        run = db.query(models.SimulationRun).filter(attribute == value).first()
        if run:
            return run


def get_simulation_runs(db: Session, **kwargs):
    query = db.query(models.SimulationRun)
    order_by = None
    if kwargs:
        for name, value in kwargs.items():
            if name == 'order_by':
                if value.startswith('-'):
                    direction = 'desc'
                    value = value[1:]
                else:
                    direction = 'asc'
                attribute = getattr(models.SimulationRun, value)
                if direction == 'asc':
                    order_by = attribute.asc()
                else:
                    order_by = attribute.desc()
            else:
                attribute = getattr(models.SimulationRun, name)
                if attribute:
                    query = query.filter(attribute.contains(value))

        if order_by is not None:
            query = query.order_by(order_by)

    runs = query.all()
    if runs:
        return runs
    else:
        return []


def create_simulation_run(db: Session, name: str, machine: models.Machine):
    run = models.SimulationRun(machine_id=machine.id, loss=-1, name=name)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_or_create_simulation_run(db: Session, name: str, machine: models.Machine):
    try:
        simulation_run = create_simulation_run(db, name, machine)
    except IntegrityError:
        db.rollback()
        simulation_run = get_simulation_run(db, name)

    return simulation_run


def delete_simulation_run(db: Session, run_name: str):
    db_user = get_simulation_run(db, run_name)
    db.delete(db_user)
    db.commit()

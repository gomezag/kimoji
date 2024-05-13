import pytest
import requests

from sqlalchemy.exc import IntegrityError

from lib import schemas
from lib.auth import get_password_hash
from lib.crud import create_user, delete_user, get_user, get_or_create_machine, delete_machine
from lib.db import SessionLocal


HOSTNAME = 'localhost'
API_PORT = '8000'
WS_PORT = '3000'


@pytest.fixture(scope='session')
def website():
    return "".join(['http://', HOSTNAME, ':', API_PORT])


@pytest.fixture(scope='session')
def wss():
    return "".join(['wss://', HOSTNAME, ':', WS_PORT])


@pytest.fixture(scope='session')
def test_password():
    return 'secret'


@pytest.fixture(scope='session')
def test_user(website, test_password):
    db = SessionLocal()
    user = schemas.UserCreate(username='johndoe', hashed_password=get_password_hash(test_password), email='test@test.com')
    try:
        create_user(db, user)
    except IntegrityError:
        db.rollback()
        user = get_user(db, username='johndoe')
    finally:
        db.close()
    yield user
    db = SessionLocal()
    try:
        delete_user(db, user)
    finally:
        db.close()


@pytest.fixture
def test_machine():
    db = SessionLocal()
    machine = schemas.MachineCreate(name='Test')
    try:
        machine = get_or_create_machine(db, machine)
    finally:
        db.close()
    yield machine
    db = SessionLocal()
    try:
        delete_machine(db, machine.name)
    finally:
        db.close()

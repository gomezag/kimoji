import pytest
import requests

from sqlalchemy.exc import IntegrityError

from lib import schemas
from lib.auth import get_password_hash
from lib.crud import create_user, delete_user, get_user, get_or_create_machine, delete_machine
from lib.crud import get_or_create_simulation_run, create_simulation_run, delete_simulation_run
from lib.db import SessionLocal


HOSTNAME = 'localhost'
API_PORT = '8000'
WS_PORT = '3000'


@pytest.fixture(scope='session')
def db():
    db = SessionLocal()
    yield db
    db.close()


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
def test_user(db, website, test_password):
    user = schemas.UserCreate(username='johndoe', hashed_password=get_password_hash(test_password), email='test@test.com')
    try:
        create_user(db, user)
    except IntegrityError:
        db.rollback()
        user = get_user(db, username='johndoe')

    yield user
    db = SessionLocal()
    delete_user(db, user)


@pytest.fixture
def machine(db):
    machine = schemas.MachineCreate(name='Test')
    machine = get_or_create_machine(db, machine)
    yield machine
    delete_machine(db, machine.name)


@pytest.fixture
def simulation_runs(db, machine):
    n_runs = 2
    run_names = [f'Test{n}' for n in range(n_runs)]
    runs = []
    for name in run_names:
        run = get_or_create_simulation_run(db, name, machine)
        runs.append(run)

    yield runs

    for run in runs:
        delete_simulation_run(db, run)

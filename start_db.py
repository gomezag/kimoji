import logging

from kimoji.lib.auth import get_password_hash
from kimoji.lib.crud import create_user, create_machine, get_user, get_machines
from kimoji.lib.db import SessionLocal
from kimoji.lib.schemas import UserCreate, MachineCreate

logger = logging.getLogger('starter')

if __name__ == '__main__':
    logger.info('Running starter')
    db = SessionLocal()
    if not get_user(db, 'admin'):
        logger.info('Creating admin user')
        create_user(db, UserCreate(username='admin', hashed_password=get_password_hash('admin'), email='admin@admin'))

    if not get_machines(db):
        logger.info('Creating test machine')
        create_machine(db, MachineCreate(name='abc'))

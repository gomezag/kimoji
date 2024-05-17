import logging
import requests
import time

from kimoji.lib.auth import get_password_hash
from kimoji.lib.crud import create_user, create_machine, get_user, get_machines
from kimoji.lib.db import SessionLocal
from kimoji.lib.schemas import UserCreate, MachineCreate

logger = logging.getLogger('kimoji')

if __name__ == '__main__':
    logger.info('Running starter')
    start_time = time.time()
    while True:
        try:
            response = requests.get('http://localhost:8000', timeout=60)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            print("Server is not up yet.")
        if time.time() - start_time > 60:
            raise requests.Timeout('Timed out while waiting for server to be alive.')
        time.sleep(1)
    db = SessionLocal()
    if not get_user(db, 'admin'):
        logger.info('Creating admin user')
        create_user(db, UserCreate(username='admin', hashed_password=get_password_hash('admin'), email='admin@admin'))

    if not get_machines(db):
        logger.info('Creating test machine')
        create_machine(db, MachineCreate(name='abc'))

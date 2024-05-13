import pytest
import urllib.parse as urlparse


HOSTNAME = 'localhost'
API_PORT = '8080'
WS_PORT = '3000'


@pytest.fixture(scope='session')
def website():
    return "".join(['http://', HOSTNAME, ':', API_PORT])


@pytest.fixture(scope='session')
def wss():
    return "".join(['wss://', HOSTNAME, ':', WS_PORT])

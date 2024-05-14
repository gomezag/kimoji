import json
import pytest
import requests
import urllib.parse as urlparse
import websocket

from lib import schemas


@pytest.fixture(scope='module')
def auth_header(website, test_user, test_password):
    uri = '/token'
    data = {
        'username': test_user.username,
        'password': test_password
    }
    r = requests.post(urlparse.urljoin(website, uri), data=data)

    assert r.status_code == 200
    data = json.loads(r.content)

    assert type(data.get('access_token')) == str
    assert data.get('token_type') == 'bearer'

    header = {
        'Authorization': f'Bearer {data.get("access_token")}'
    }
    return header


def test_login(website, test_user, test_password, auth_header):
    uri = 'users/me'
    r = requests.get(urlparse.urljoin(website, uri), headers=auth_header)
    assert r.status_code == 200
    data = json.loads(r.content)
    assert data['username'] == test_user.username
    assert data['email'] == test_user.email


def test_get_machine_list(website, machine, auth_header):
    uri = '/machines'
    r = requests.get(urlparse.urljoin(website, uri), headers=auth_header)

    assert r.status_code == 200
    data = json.loads(r.content)
    machines = [schemas.Machine(**machine) for machine in data]
    assert schemas.Machine(**machine.__dict__) in machines


def test_get_run_list(db, website, simulation_runs, auth_header):
    uri = 'runs'
    r = requests.get(urlparse.urljoin(website, uri), headers=auth_header)
    assert r.status_code == 200
    data = json.loads(r.content)
    runs = [schemas.SimulationRun(**run) for run in data]

    for run in simulation_runs:
        db.refresh(run)
        assert schemas.SimulationRun(**run.__dict__) in runs


def test_get_filtered_run_list(db, website, simulation_runs, auth_header, run_names):
    uri = '/runs'
    lookup = 'Test'
    r = requests.get(urlparse.urljoin(website, uri),
                     params={'name': lookup},
                     headers=auth_header
                     )
    assert r.status_code == 200
    data = json.loads(r.content)
    names = [schemas.SimulationRun(**run).name for run in data]
    assert [e for e in names if e in run_names] == [e for e in run_names if lookup in e]


def test_get_ordered_run_list(website, simulation_runs, auth_header, run_names):
    uri = 'runs'
    params = {'order_by': '-name'}
    r = requests.get(urlparse.urljoin(website, uri),
                     params=params,
                     headers=auth_header)

    assert r.status_code == 200
    data = json.loads(r.content)
    names = [el['name'] for el in data]
    assert [e for e in names if e in run_names] == sorted(run_names, reverse=True)


def test_post_run(website):
    uri = '/v1/api/run'
    data = {
        'machine': '1',
        'simulation': 'test_sim'
    }
    r = requests.post(urlparse.urljoin(website, uri), data)

    assert r.status_code == 200


def test_get_run_detail(website):
    uri = '/v1/api/run/test_sim'
    r = requests.get(urlparse.urljoin(website, uri))

    assert r.status_code == 200


def test_subscribe_to_run_socket(wss):
    uri = '/v1/api/run/test_sim'
    ws = websocket.WebSocket()
    ws.connect(urlparse.urljoin(websocket, uri))

    try:
        ws.recv()
    finally:
        ws.close()

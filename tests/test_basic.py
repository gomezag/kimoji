import json
import requests
import urllib.parse as urlparse
import websocket


def test_login(website, test_user, test_password):
    login_uri = '/token'
    profile_uri = 'users/me'
    data = {
        'username': test_user.username,
        'password': test_password
    }
    r = requests.post(urlparse.urljoin(website, login_uri), data=data)

    assert r.status_code == 200
    data = json.loads(r.content)

    assert type(data.get('access_token')) == str
    assert data.get('token_type') == 'bearer'

    header = {
        'Authorization': f'Bearer {data.get("access_token")}'
    }
    r = requests.get(urlparse.urljoin(website, profile_uri), headers=header)
    assert r.status_code == 200
    data = json.loads(r.content)
    assert data['username'] == test_user.username
    assert data['email'] == test_user.email


def test_get_run_list(website):
    uri = '/v1/api/runs'
    r = requests.get(urlparse.urljoin(website, uri))

    assert r.status_code == 200


def test_get_filtered_run_list(website):
    uri = '/v1/api/runs'
    r = requests.get(
                         urlparse.urljoin(website, uri),
                         params={
                             'filters': [{
                                 'field': 'name',
                                 'type': 'contains',
                                 'keyword': 'Windows'
                                }
                             ]
                         }
                     )
    assert r.status_code == 200


def test_get_ordered_run_list(website):
    uri = '/v1/api/runs'
    r = requests.get(urlparse.urljoin(website, uri),
                     params={
                         'order_by': 'name'
                     })

    assert r.status_code == 200


def test_get_machine_list(website):
    uri = '/v1/api/machines'
    r = requests.get(urlparse.urljoin(website, uri))

    assert r.status_code == 200


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

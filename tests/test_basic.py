import requests
import urllib.parse as urlparse
import websocket

TEST_USER = 'johndoe'
TEST_PASSWORD = 'secret'


def test_login(website):
    uri = '/login'
    data = {
        'username': TEST_USER,
        'password': TEST_PASSWORD
    }
    r = requests.post(urlparse.urljoin(website, uri), data=data)

    assert r.status_code == 200


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

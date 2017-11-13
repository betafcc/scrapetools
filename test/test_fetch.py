import pytest

from .util import start_server

from scrapetools.fetch import fetch
from scrapetools.util import run


@pytest.fixture(scope='module')
def server():
    server_process = start_server()
    yield
    server_process.terminate()


def test_fetch_one(server):
    local_url = 'http://localhost:5000'

    url, resp, err = run(fetch(local_url))

    assert local_url == url
    assert resp
    assert err is None

    url, resp, err = run(fetch('http://localhost:5000/foo'))

    assert resp is None
    assert isinstance(err, Exception)

    url, resp, err = run(fetch('malformedurl'))

    assert resp is None
    assert isinstance(err, Exception)


def test_fetch_all(server):
    index = 'http://localhost:5000'
    home  = 'http://localhost:5000/home.html'

    resps = run(fetch([index, home]))

    assert len(resps) == 2

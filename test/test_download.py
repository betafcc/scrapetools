import pytest

from shutil import rmtree
from os import mkdir, listdir
from os.path import abspath, dirname, join

from .util import start_server
from scrapetools.util import run

from scrapetools.download import download


__dirname = abspath(dirname(__file__))

DOWNLOAD_DIR = abspath(join(__dirname, 'downloaded'))


local_url = 'http://localhost:5000'

files = [
    'brown.txt',
    'genesis.txt',
    'lorem.txt',
]

urls = {
    file: f'{local_url}/download/{file}'
    for file in files
}


@pytest.fixture(scope='module')
def server():
    server_process = start_server()
    yield
    server_process.terminate()


@pytest.fixture
def download_dir():
    mkdir(DOWNLOAD_DIR)
    yield
    rmtree(DOWNLOAD_DIR)


def test_download_one(server, download_dir):
    assert len(listdir(DOWNLOAD_DIR)) == 0

    run(download(urls['brown.txt'], DOWNLOAD_DIR))

    ls = listdir(DOWNLOAD_DIR)
    assert len(ls) == 1
    assert ls[0] == 'brown.txt'


def test_download_all(server, download_dir):
    assert len(listdir(DOWNLOAD_DIR)) == 0

    run(download(urls.values(), DOWNLOAD_DIR))

    ls = listdir(DOWNLOAD_DIR)
    assert len(ls) == len(urls)
    assert set(ls) == set(urls.keys())


def test_download_all_return(server, download_dir):
    assert len(listdir(DOWNLOAD_DIR)) == 0

    ret = run(download(urls.values(), DOWNLOAD_DIR))

    assert ret is None


def test_download_all_dict_named(server, download_dir):
    assert len(listdir(DOWNLOAD_DIR)) == 0

    run(download({
        urls['brown.txt']   : join(DOWNLOAD_DIR, 'A.txt'),
        urls['genesis.txt'] : join(DOWNLOAD_DIR, 'B.txt'),
        urls['lorem.txt']   : join(DOWNLOAD_DIR, 'C.txt'),
    }))

    ls = listdir(DOWNLOAD_DIR)
    assert len(ls) == 3
    assert set(ls) == {'A.txt', 'B.txt', 'C.txt'}

import pytest

from .util import start_server

from scrapetools.scrape import scrape


@pytest.fixture(scope='module')
def server():
    server_process = start_server()
    yield
    server_process.terminate()


def test_parse():
    scraped = scrape('<div>Hello</div>', xpath='.//text()')
    assert scraped[0] == 'Hello'

    ul = '''
    <ul>
        <li>1</li>
        <li>2</li>
        <li>3</li>
    </ul>
    '''

    assert len(scrape(ul, 'li')) == 3

    # auto-partial version
    assert len(scrape(css='li')(ul)) == len(scrape(ul, 'li'))


def test_request(server):
    scraped = scrape('http://localhost:5000')

    assert scraped


def test_request_and_parse(server):
    scraped = scrape(
        'http://localhost:5000',
        css='body',
        xpath='.//text()'
    )

    assert scraped
    assert len(scraped) == 1
    assert scraped[0].strip() == 'Hello World'

import pytest

import os
from scrapetools.util import run, url_basename, sensible_download_path


def test_run():
    async def foo():
        return 10

    assert run(foo()) == 10


@pytest.mark.parametrize('url, expected', [
    ('http://www.foo.com/dlstatic/16103010.pdf', '16103010.pdf'),
])
def test_url_basename(url, expected):
    assert url_basename(url) == expected


@pytest.mark.parametrize('url, path, expected', [
    (
        'http://www.foo.com/dlstatic/16103010.pdf',
        None,
        os.path.join(os.path.abspath('.'), '16103010.pdf')
    ),
    (
        'http://www.foo.com/dlstatic/16103010.pdf',
        '..',
        os.path.join(os.path.abspath('..'), '16103010.pdf')
    ),
])
def test_sensible_download_path(url, path, expected):
    assert sensible_download_path(url, path) == expected

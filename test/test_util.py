import pytest

import os
import shutil
from scrapetools.util import (
    run, url_basename, sensible_download_path, mkdirdeep
)


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


def test_mkdirdeep():
    base_path = os.path.join(
        os.path.dirname(__file__),
        'mkdirdeep_test'
    )
    deep_path = os.path.join(
        base_path,
        'a', 'b', 'c', 'd'
    )

    assert not os.path.isdir(base_path)

    try:
        mkdirdeep(deep_path)
        assert os.path.isdir(deep_path)
    except AssertionError as e:
        raise e
    finally:
        try:
            shutil.rmtree(base_path)
        except FileNotFoundError:
            pass

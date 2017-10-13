from typing import TypeVar, Awaitable

import os
import posixpath
import asyncio
from urllib.parse import urlparse


A = TypeVar('A')


def run(coro: Awaitable[A]) -> A:
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


def sensible_download_path(url  : str,
                           path : str = None
                           ) -> str:
    if not path:
        path = '.'

    path = os.path.abspath(path)

    if os.path.isdir(path):
        return os.path.join(path, url_basename(url))

    return path


def url_basename(url: str) -> str:
    return posixpath.basename(urlparse(url).path)

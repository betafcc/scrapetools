from typing import TypeVar, Awaitable

import os
import posixpath
import asyncio
from urllib.parse import urlparse
from itertools import accumulate


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


def mkdirdeep(path: str) -> None:
    sections = path.split(os.sep)  # type: ignore

    # If path is absolute, first section will be empty
    if sections[0] == '':
        sections[0] = os.sep

    partials = list(
        accumulate(
            sections,
            lambda acc, n: acc + os.sep + n
        )
    )

    for partial_path in partials:
        try:
            os.mkdir(partial_path)
        except FileExistsError:
            pass

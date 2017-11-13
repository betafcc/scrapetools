from typing import (  # NOQA
    Iterator, Any, Generic, TypeVar,
    Callable, Union, Iterable, Awaitable,
    List,
)
import asyncio
from functools import wraps

import aiohttp  # type: ignore
from tqdm import tqdm  # type: ignore

from .response import Response
from .util import run


A = TypeVar('A')


__all__ = [
    'fetch', 'fetch_sync',
]


bar_options = {
    'bar_format'    : '{l_bar}{bar}|{n_fmt}/{total_fmt}',
    'dynamic_ncols' : True,
    'unit_scale'    : True,
    'leave'         : True,
}


def fetch(urls           : Union[str, Iterable[str]],
          session        : aiohttp.ClientSession = None,
          show_progress  : bool = False,
          max_concurrent : int  = 1000,
          ) -> Union[Awaitable['Response'],
                     Awaitable[List['Response']]]:
    if isinstance(urls, str):
        return fetch_one(url=urls, session=session)
    return fetch_all(**locals())


def fetch_sync(*args    : Any,
               **kwargs : Any,
               ) -> Union['Response',
                          List['Response']]:
    return run(fetch(*args, **kwargs))  # type: ignore


def responsify(f: Callable[..., Awaitable[A]]
               ) -> Callable[..., Awaitable['Response[A]']]:
    @wraps(f)
    async def _(url  : str,
                *args: Any,
                **kwargs: Any,
                ) -> Response[A]:
        try:
            return Response(url, await f(url, *args, **kwargs))
        except Exception as error:
            return Response(url, error=error)

    return _


@responsify
def fetch_one(url      : str,
              session  : aiohttp.ClientSession  = None,
              ) -> Awaitable['Response']:
    return _fetch_one(url, session)


async def _fetch_one(url      : str,
                     session  : aiohttp.ClientSession  = None,
                     response : aiohttp.ClientResponse = None,
                     ) -> 'Response':
    if not session:
        async with aiohttp.ClientSession() as session:
            return await _fetch_one(url,
                                    session=session,
                                    response=response,
                                    )

    if not response:
        async with session.get(url) as response:
            return await _fetch_one(url,
                                    session=session,
                                    response=response,
                                    )

    assert response.status == 200, 'Response status is not 200'

    return await response.text()


def fetch_all(urls           : List[str],
              session        : aiohttp.ClientSession = None,
              show_progress  : bool = False,
              max_concurrent : int  = 1000,
              ) -> Awaitable[List['Response']]:
    return _fetch_all(**locals())


async def _fetch_all(urls           : List[str],
                     session        : aiohttp.ClientSession = None,
                     show_progress  : bool = False,
                     max_concurrent : int  = 1000,
                     pbar           : tqdm = None,
                     ):
    arguments = locals()

    if not session:
        async with aiohttp.ClientSession() as session:
            arguments.update(session=session)
            return await _fetch_all(**arguments)

    if show_progress and not pbar:
        urls = list(urls)  # need to unpack for len

        with tqdm(**bar_options, total=len(urls)) as pbar:
            arguments.update(urls=urls, pbar=pbar)
            return await _fetch_all(**arguments)

    semaphore = asyncio.Semaphore(max_concurrent)

    async def bound_fetch_one(url : str) -> 'Response':
        async with semaphore:
            result = await fetch_one(url=url, session=session)

        if show_progress:
            pbar.update(1)
        return result

    return await asyncio.gather(
        *map(bound_fetch_one, urls),
        return_exceptions=True,
    )

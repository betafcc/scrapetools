from typing import (  # NOQA
    Iterator, Any, Generic, TypeVar,
    Callable, Union, Iterable, Awaitable,
    List,
)
import asyncio

import aiohttp  # type: ignore
from tqdm import tqdm  # type: ignore

from .util import run
from .meta import Show


__all__ = [
    'fetch', 'fetch_sync',
]


bar_options = {
    'bar_format'    : '{l_bar}{bar}|{n_fmt}/{total_fmt}',
    'dynamic_ncols' : True,
    'unit_scale'    : True,
    'leave'         : True,
}


A = TypeVar('A')
B = TypeVar('B')


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


async def fetch_one(url     : str,
                    session : aiohttp.ClientSession = None,
                    ) -> 'Response':
    if not session:
        async with aiohttp.ClientSession() as session:
            return await fetch_one(url, session=session)

    async with session.get(url) as response:
        try:
            assert response.status == 200
            result = await response.text()
            return Response(url, result)
        except Exception as err:
            return Response(url, error=err)


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


class Response(Generic[A], Show):
    url    : str
    result : A
    error  : Exception

    def __init__(self,
                 url    : str,
                 result : A = None,
                 error  : Exception = None,
                 ) -> None:
        self.url    = url
        self.result = result
        self.error  = error

    # __iter__ used mostly for destructuring eg:
    # url, cont, _ = resp
    def __iter__(self) -> Iterator[Any]:
        yield self.url
        yield self.result
        yield self.error

    def fmap(self,
             f : Callable[[A], B]
             ) -> 'Union[Response[A], Response[B]]':
        if self.error is not None:
            return self
        return Response(self.url, f(self.result), self.error)

    def bind(self,
             f : Callable[[A], 'Response[B]']
             ) -> 'Union[Response[A], Response[B]]':
        if self.error is not None:
            return self
        return f(self.result)

    def fold(self,
             on_result : Callable[[A], B] = None,
             on_error  : Callable[[Exception], B] = None,
             ) -> Union[A, B, Exception]:
        if self.error is not None:
            if on_error is None:
                return self.error
            return on_error(self.error)

        if self.result is not None:
            if on_result is None:
                return self.result
            return on_result(self.result)

        raise TypeError('Either result or error must not be None')

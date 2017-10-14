# scrapetools

Utilities I use for Web Scrapping, useful for exploration in the REPL

Install
-------

```sh
git clone https://github.com/betafcc/scrapetools.git
cd scrapetools
pip install .
```

## Functions:

### scrape
```py
scrape(
    data     : Union[Url, Html, xml.html.HtmlElement] = None,
    css      : str  = None,
    xpath    : str  = None,
    base_url : str  = None,
    flatten  : bool = True,
) -> Union[Matches, partial]
```
General utility for querying css selector and/or xpath


#### usage
```py
from scrapetools import scrape


>>> scrape('<div>Hello World</div>', xpath='.//text()')
['Hello World']
# Parse Html string and returns list of the query results


>>> links = scrape('http://www.python.org', css='a')
# fetch and parse all links in the html,
# returns a list with the matches


>>> links_text = scrape('http://www.python.org', css='a', xpath='.//text()')
# can use css selector and xpath combined
# that will first match css and them run xpath on each



>>> get_links_text = scrape(css='a', xpath='.//text()')
>>> get_links_text('http://www.python.org')
# Can be used with partial aplication
```

### fetch and fetch_sync
```py
fetch(
    urls           : Union[str, Iterable[str]],
    session        : aiohttp.ClientSession = None,
    show_progress  : bool = False,
    max_concurrent : int  = 1000,
) -> Union[Awaitable[Response], Awaitable[List[Response]]]
```

Efficiently fetches one url or a list of urls,implementation
based on ["Making 1 million requests with python-aiohttp"](
https://pawelmhm.github.io/asyncio/python/aiohttp/2016/04/22/asyncio-aiohttp.html)

#### usage
```py
>>> import asyncio
>>> from scrapetools import fetch, fetch_sync
>>> coro = fetch('http://www.python.org')
>>> loop = asyncio.get_event_loop()

>>> resp = loop.run_until_complete(coro)
>>> url, result, error = resp
# returns a 'Response' object, which is destructurable

>>> url, result, error = fetch_sync('http://www.python.org')
# convenience version that runs and returns automatically


>>> coro = fetch([
    'http://www.python.org',
    'http://www.twitter.com',
    'http://www.reuters.com',
    'http://www,cnbc.com',
    'http://www.yahoo.com',
    'http://www.pypy.com',
], show_progress=True)
# optionally, show a progress bar


>>> loop.run_until_complete(coro)
# Will efficiently fetch all urls asynchronously
# and return a list of responses ordered as the input
```

Since it returns a 'Response' object, the result won't blow up in your face when a exception is raised.

Response contains 'url', 'result' and 'error' atributes, if no error ocurred, 'error' will be None, else, 'result' will be None and 'error' will contain the Exception object raised.

Response also is a poor version of 'Either Monad', that is, it contains a smart 'fmap' function, that will run only on sucess:

```py
>>> resp = loop.run_until_complete(fetch('http://www.python.org'))
>>> resp.fmap(scrap(css='a')) # If it failed, won't try to map

>>> resp.fold(lambda res: print(res), lambda err: print('Failed'))
# run first function on sucess, second on exception

>>> result_or_exception = resp.fold()
# returns either the content (on sucess) or the exception object (on failure)

>>> parsed_result = resp.fold(scrap(css='a'))
# returns the queried result on fetch sucess, the exception object on failure
```

### download and download_sync
```py
download(
    urls           : Union[str, Iterable[str]],
    path           : str = None,
    session        : aiohttp.ClientSession = None,
    show_progress  : bool = False,
    max_concurrent : int  = 5,
) -> Awaitable[None]:
```

#### usage
```py
>>> coro = download('https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz', show_progress=True)
>>> loop.run_until_complete(coro)
# will download 'Python-3.6.3.tgz' in the current directory

download_sync('https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz', '../downloads', show_progress=True)
## will download 'Python-3.6.3.tgz' in the relative path provided

download_sync('https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz', '../downloads/python3.tgz', show_progress=True)
## will download as 'python3.tgz' in the relative path provided


download_sync([
  'https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz',
  'https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz',
  'https://www.python.org/ftp/python/3.6.3/python-3.6.3-macosx10.6.pkg',
  'https://www.python.org/ftp/python/3.6.3/python363.chm',
], '../downloads', show_progress=True)
# will concurrently download all files to the provided path,
# keeping original file name
```
### fmap
```py
fmap(f: Callable[[A], B], obj: Functor[A]) -> Functor[B]
fmap(f: Callable[[A], B], obj: List[A]) -> List[B]
fmap(f: Callable[[A], B], obj: Tuple[A, ...]) -> Tuple[B, ...]
fmap(f: Callable[[A], B], obj: Awaitable[A]) -> Awaitable[B]
fmap(f: Callable[[A], B], obj: Generator[A]) -> Generator[B]
fmap(f: Callable[[A], B], obj: Iterator[A]) -> Iterator[B]
fmap(f: Callable[[A], B], obj: Callable[..., A]) -> Callable[..., B]
```
Utility that simulates functor-map functionality for built-in types
(that is, will try to maintain the original 'container' type)

#### usage
```py
>>> fmap(lambda x: x*x, [1, 2, 3, 4, 5])
[1, 4, 9, 16, 25]

>>> fmap(lambda x: x*x, (1, 2, 3, 4, 5))
(1, 4, 9, 16, 25)

>>> async def foo(): return 10
>>> loop.run_until_complete(foo())
10
>>> coro = fmap(lambda x: x*x, foo())
>>> loop.run_until_complete(coro)
100

# Can be used with partial application:
>>> square_all = fmap(lambda x: x*x)
>>> square_all([2, 3, 4])
[4, 9, 16]

>>> fmap(fmap(lambda x: x*x), ([1, 2, 3], [4, 5, 6]))
([1, 4, 9], [16, 25, 36])

```

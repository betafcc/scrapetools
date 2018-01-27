import asyncio

from scrapetools.fmap import fmap
from scrapetools.util import run


def test_fmap():
    l  = [1, 2, 3, 4, 5]
    sq = lambda x: x * x
    assert fmap(sq, l) == [1, 4, 9, 16, 25]
    # test auto curring
    assert fmap(sq)(l) == fmap(sq, l)

    t = (1, 2, 3, 4, 5)
    assert fmap(sq, t) == (1, 4, 9, 16, 25)

    f, g = lambda x: x + 1, lambda x: x * x
    # fmapping functions should be equivalent to compose
    assert fmap(f, g)(5) == 26

    async def foo():
        return 10
    assert run(fmap(lambda x: x * x, foo())) == 100

    async def foo():
        return 10
    assert run(fmap(lambda x: x * x, asyncio.ensure_future(foo()))) == 100

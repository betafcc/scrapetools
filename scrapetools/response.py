from typing import Generic, TypeVar, Iterator, Any, Callable, Union

from .meta import Show


A = TypeVar('A')
B = TypeVar('B')


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

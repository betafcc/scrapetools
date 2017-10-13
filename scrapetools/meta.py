from typing import Any
from abc import ABCMeta


class Show(metaclass=ABCMeta):
    """
    This metaclass gives a reasonable __repr__
    method to a class, just caches the constructor
    arguments so it can show how it was called

    eg:

    class A(Show):
        def __init__(self, *args):
            pass

    >>> repr(A(1, 2, 3, 4))
    'A(1, 2, 3, 4)'
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        instance = super().__new__(cls)

        setattr(instance,
                'constructor_arguments',
                {'args': args, 'kwargs': kwargs})

        return instance

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        args = ', '.join(
            repr(arg) for arg in
            self.constructor_arguments['args']  # type: ignore
        )

        kwargs = ', '.join(
            f'{key}={repr(arg)}' for key, arg in
            self.constructor_arguments['kwargs'].items()  # type: ignore
        )

        allargs = ''
        if args:
            allargs += args
            if kwargs:
                allargs += ', '
        if kwargs:
            allargs += kwargs

        return f'{cls}({allargs})'

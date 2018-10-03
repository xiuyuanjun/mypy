from typing import (
    Generic, TypeVar, Iterator, Callable, Iterable, Any, Mapping, Optional, Generator,
)

from mypy.contextlib import _GeneratorContextManager, ContextManager
from functools import wraps

from typing import (
    Generic, TypeVar, Iterator, Callable, Iterable, Any, Mapping, Optional, Generator,
)
_T = TypeVar('_T')

def contextmanager(func: Callable[..., Iterator[_T]]) -> Callable[..., ContextManager[_T]]:
    """@contextmanager decorator.

    Typical usage:

        @contextmanager
        def some_generator(<arguments>):
            <setup>
            try:
                yield <value>
            finally:
                <cleanup>

    This makes this:

        with some_generator(<arguments>) as <variable>:
            <body>

    equivalent to this:

        <setup>
        try:
            <variable> = <value>
            <body>
        finally:
            <cleanup>
    """
    @wraps(func)
    def helper(*args: Any, **kwds: Any) -> _GeneratorContextManager[_T]:
        return _GeneratorContextManager(func, args, kwds)
    return helper

"""Utilities for with-statement contexts.  See PEP 343."""
import abc
import sys
from collections import deque
from functools import wraps
from contextlib import AbstractContextManager

from typing import (
    Generic, TypeVar, Iterator, Callable, Iterable, Any, Mapping, Optional, Generator,
)
MYPY = False
if MYPY:
    from typing import Type

# lurr?
from typing import ContextManager as ContextManager

if sys.version_info >= (3, 6):
    from typing import ContextManager as AbstractContextManager

# __all__ = ["contextmanager"]

_T = TypeVar('_T')

# class ContextDecorator(object):
#     "A base class or mixin that enables context managers to work as decorators."

#     def _recreate_cm(self):
#         """Return a recreated instance of self.

#         Allows an otherwise one-shot context manager like
#         _GeneratorContextManager to support use as
#         a decorator via implicit recreation.

#         This is a private interface just for _GeneratorContextManager.
#         See issue #11647 for details.
#         """
#         return self

#     def __call__(self, func):
#         @wraps(func)
#         def inner(*args, **kwds):
#             with self._recreate_cm():
#                 return func(*args, **kwds)
#         return inner


class _GeneratorContextManagerBase(Generic[_T]):
    """Shared functionality for @contextmanager and @asynccontextmanager."""

    def __init__(self,
                 func: Callable[..., Iterator[_T]],
                 args: Iterable[Any],
                 kwds: Mapping[str, Any]) -> None:
        self.gen = func(*args, **kwds)
        # self.func, self.args, self.kwds = func, args, kwds
        # Issue 19330: ensure context manager instances have good docstrings
        # doc = getattr(func, "__doc__", None)
        # if doc is None:
        #     doc = type(self).__doc__
        # self.__doc__ = doc
        # Unfortunately, this still doesn't provide good help output when
        # inspecting the created context manager instances, since pydoc
        # currently bypasses the instance docstring and shows the docstring
        # for the class instead.
        # See http://bugs.python.org/issue19404 for more details.


class _GeneratorContextManager(_GeneratorContextManagerBase[_T],
                               AbstractContextManager[_T],
#                               ContextDecorator
):
    """Helper for @contextmanager decorator."""

    # def _recreate_cm(self):
    #     # _GCM instances are one-shot context managers, so the
    #     # CM must be recreated each time a decorated function is
    #     # called
    #     return self.__class__(self.func, self.args, self.kwds)

    def __enter__(self) -> _T:
        try:
            return next(self.gen)
        except StopIteration:
            raise RuntimeError("generator didn't yield") from None

    def __exit__(self, type: 'Optional[Type[BaseException]]',
                 value: Optional[BaseException], traceback: Optional[Any]) -> bool:
        if type is None:
            try:
                next(self.gen)
            except StopIteration:
                return False
            else:
                raise RuntimeError("generator didn't stop")
        else:
            if value is None:
                # Need to force instantiation so we can reliably
                # tell if we get the same exception back
                value = type()
            try:
                # The typeshed contextlib stubs allow an Iterable and
                # that is what all of our code does, but Iterable
                # doesn't have throw. Oh well.
                self.gen.throw(type, value, traceback)  # type: ignore
            except StopIteration as exc:
                # Suppress StopIteration *unless* it's the same exception that
                # was passed to throw().  This prevents a StopIteration
                # raised inside the "with" statement from being suppressed.
                return exc is not value
            except RuntimeError as exc:
                # Don't re-raise the passed in exception. (issue27122)
                if exc is value:
                    return False
                # Likewise, avoid suppressing if a StopIteration exception
                # was passed to throw() and later wrapped into a RuntimeError
                # (see PEP 479).
                if type is StopIteration and exc.__cause__ is value:
                    return False
                raise
            except:
                # only re-raise if it's *not* the exception that was
                # passed to throw(), because __exit__() must not raise
                # an exception unless __exit__() itself failed.  But throw()
                # has to raise the exception to signal propagation, so this
                # fixes the impedance mismatch between the throw() protocol
                # and the __exit__() protocol.
                #
                # This cannot use 'except BaseException as exc' (as in the
                # async implementation) to maintain compatibility with
                # Python 2, where old-style class exceptions are not caught
                # by 'except BaseException'.
                if sys.exc_info()[1] is value:
                    return False
                raise
            raise RuntimeError("generator didn't stop after throw()")


# def contextmanager(func: Callable[..., Iterator[_T]]) -> Callable[..., ContextManager[_T]]:
#     """@contextmanager decorator.

#     Typical usage:

#         @contextmanager
#         def some_generator(<arguments>):
#             <setup>
#             try:
#                 yield <value>
#             finally:
#                 <cleanup>

#     This makes this:

#         with some_generator(<arguments>) as <variable>:
#             <body>

#     equivalent to this:

#         <setup>
#         try:
#             <variable> = <value>
#             <body>
#         finally:
#             <cleanup>
#     """
#     @wraps(func)
#     def helper(*args: Any, **kwds: Any) -> _GeneratorContextManager[_T]:
#         return _GeneratorContextManager(func, args, kwds)
#     return helper

from mypy._contextlib import contextmanager

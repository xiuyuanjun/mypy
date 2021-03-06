"""This module makes it possible to use mypy as part of a Python application.

Since mypy still changes, the API was kept utterly simple and non-intrusive.
It just mimics command line activation without starting a new interpreter.
So the normal docs about the mypy command line apply.
Changes in the command line version of mypy will be immediately useable.

Just import this module and then call the 'run' function with a parameter of
type List[str], containing what normally would have been the command line
arguments to mypy.

Function 'run' returns a Tuple[str, str, int], namely
(<normal_report>, <error_report>, <exit_status>),
in which <normal_report> is what mypy normally writes to sys.stdout,
<error_report> is what mypy normally writes to sys.stderr and exit_status is
the exit status mypy normally returns to the operating system.

Any pretty formatting is left to the caller.

The 'run_dmypy' function is similar, but instead mimics invocation of
dmypy.

Note that these APIs don't support incremental generation of error
messages.

Trivial example of code using this module:

import sys
from mypy import api

result = api.run(sys.argv[1:])

if result[0]:
    print('\nType checking report:\n')
    print(result[0])  # stdout

if result[1]:
    print('\nError report:\n')
    print(result[1])  # stderr

print('\nExit status:', result[2])

"""

import sys
from io import StringIO
from typing import List, Tuple, Union, TextIO, Callable
from mypy_extensions import DefaultArg


def _run(main_wrapper: Callable[[TextIO, TextIO], None]) -> Tuple[str, str, int]:

    stdout = StringIO()
    stderr = StringIO()

    try:
        main_wrapper(stdout, stderr)
        exit_status = 0
    except SystemExit as system_exit:
        exit_status = system_exit.code

    return stdout.getvalue(), stderr.getvalue(), exit_status


def run(args: List[str]) -> Tuple[str, str, int]:
    # Lazy import to avoid needing to import all of mypy to call run_dmypy
    from mypy.main import main
    return _run(lambda stdout, stderr: main(None, args=args,
                                            stdout=stdout, stderr=stderr))


def run_dmypy(args: List[str]) -> Tuple[str, str, int]:
    from mypy.dmypy import main
    return _run(lambda stdout, stderr: main(args))

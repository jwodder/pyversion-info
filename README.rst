.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://github.com/jwodder/pyversion-info/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/pyversion-info/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/pyversion-info/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/pyversion-info

.. image:: https://img.shields.io/pypi/pyversions/pyversion-info.svg
    :target: https://pypi.org/project/pyversion-info/

.. image:: https://img.shields.io/github/license/jwodder/pyversion-info.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/pyversion-info>`_
| `PyPI <https://pypi.org/project/pyversion-info/>`_
| `Documentation <https://pyversion-info.readthedocs.io>`_
| `Issues <https://github.com/jwodder/pyversion-info/issues>`_
| `Changelog <https://github.com/jwodder/pyversion-info/blob/master/CHANGELOG.md>`_

Ever needed to know what Python versions were currently supported, or how many
subversions a given Python version had?  Wondering how long until a given
version came out or reached end-of-life?  Need to know what CPython versions a
given PyPy version corresponds to?  The answers to these and some other
questions can be found with this library.

``pyversion-info`` pulls its data every run from
`jwodder/pyversion-info-data <https://github.com/jwodder/pyversion-info-data>`_
on GitHub.  Prerelease versions are not (currently) included.  I promise
24-hour turnaround times for keeping the database up-to-date until I am hit by
a bus.

See `the documentation <https://pyversion-info.readthedocs.io>`_ for more
information.


Installation
============
``pyversion-info`` requires Python 3.7 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``pyversion-info`` and its dependencies::

    python3 -m pip install pyversion-info


Examples
========

(The given outputs are current as of 2021-11-04.)

Start out by fetching the database:

>>> from pyversion_info import VersionDatabase
>>> vd = VersionDatabase.fetch()

Get a list of all currently-supported CPython series:

>>> vd.cpython.supported_series()
['3.6', '3.7', '3.8', '3.9', '3.10']

When does 3.11 come out?

>>> vd.cpython.release_date("3.11")
datetime.date(2022, 10, 3)

When does 3.6 reach end-of-life?

>>> vd.cpython.eol_date("3.6")
datetime.date(2021, 12, 23)

Just how many micro versions does 3.9 have, anyway?

>>> vd.cpython.subversions("3.9")
['3.9.0', '3.9.1', '3.9.2', '3.9.3', '3.9.4', '3.9.5', '3.9.6', '3.9.7', '3.9.8', '3.9.9', '3.9.10', '3.9.11']

What major versions of PyPy are there?

>>> vd.pypy.major_versions()
['1', '2', '4', '5', '6', '7']

What CPython series do PyPy 7.3.\* support?

>>> vd.pypy.supported_cpython_series("7.3")
['2.7', '3.6', '3.7', '3.8']


Caveats
=======

The CPython database is generally only updated when an edit is made to a
release schedule PEP.  Occasionally, a deadline listed in a PEP is missed, but
the PEP is not updated for a couple days, and so for a brief period this
library will falsely report the given version as released.

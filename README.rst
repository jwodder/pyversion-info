.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://travis-ci.com/jwodder/pyversion-info.svg?branch=master
    :target: https://travis-ci.com/jwodder/pyversion-info

.. image:: https://codecov.io/gh/jwodder/pyversion-info/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/pyversion-info

.. image:: https://img.shields.io/pypi/pyversions/pyversion-info.svg
    :target: https://pypi.org/project/pyversion-info/

.. image:: https://img.shields.io/github/license/jwodder/pyversion-info.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
    :target: https://saythanks.io/to/jwodder

`GitHub <https://github.com/jwodder/pyversion-info>`_
| `PyPI <https://pypi.org/project/pyversion-info/>`_
| `Issues <https://github.com/jwodder/pyversion-info/issues>`_
| `Changelog <https://github.com/jwodder/pyversion-info/blob/master/CHANGELOG.md>`_

.. contents::
    :backlinks: top

Ever needed to know what Python versions were currently supported, or how many
subversions a given Python version had?  Wondering how long until a given
version came out or reached end-of-life?  The answers to these and some other
questions can be found with this library.

``pyversion-info`` pulls its data every run from
`jwodder/pyversion-info-data <https://github.com/jwodder/pyversion-info-data>`_
on GitHub.  Prerelease versions are not (currently) included.  I promise
24-hour turnaround times for keeping the database up-to-date until I am hit by
a bus.


Installation
============
Just use `pip <https://pip.pypa.io>`_ (You have pip, right?) to install
``pyversion-info`` and its dependencies::

    pip install pyversion-info


Examples
========

Start out by fetching the database::

    >>> from pyversion_info import get_pyversion_info
    >>> pyvinfo = get_pyversion_info()

Get a list of all currently-supported Python series::

    >>> pyvinfo.supported_series()
    ['2.7', '3.5', '3.6', '3.7']

When does 3.8 come out?

::

    >>> pyvinfo.release_date("3.8")
    datetime.date(2019, 10, 21)

When does 2.7 reach end-of-life?

::

    >>> pyvinfo.eol_date("2.7")
    datetime.date(2020, 1, 1)

Just how many micro versions does 2.7 have, anyway?

::

    >>> pyvinfo.subversions("2.7")
    ['2.7.0', '2.7.1', '2.7.2', '2.7.3', '2.7.4', '2.7.5', '2.7.6', '2.7.7', '2.7.8', '2.7.9', '2.7.10', '2.7.11', '2.7.12', '2.7.13', '2.7.14', '2.7.15', '2.7.16']


How many versions of Python 3 have been released?

::

    >>> pyvinfo.subversions("3")
    ['3.0', '3.1', '3.2', '3.3', '3.4', '3.5', '3.6', '3.7']


API
===

Versions are passed to & returned from methods as strings in the form ``"X"``
(a major version), ``"X.Y"`` (a minor version), or ``"X.Y.Z"`` (a micro
version).

All dates are returned as ``datetime.date`` objects.

``PyVersionInfo``
-----------------
A class for querying Python versions and their release & EOL dates

``PyVersionInfo(data)``
   Construct a new ``PyVersionInfo`` object from a `dict` containing version
   release dates and series EOL dates structured in accordance with `this
   JSON Schema
   <https://raw.githubusercontent.com/jwodder/pyversion-info-data/master/pyversion-info-data.schema.json>`_

``pyvinfo.eol_date(series)``
   Returns the end-of-life date of the given Python version series (i.e., a
   minor version like 3.5).  The return value may be `None`, indicating that
   the series is not yet end-of-life and its end-of-life date is unknown or
   undetermined.  The return value may alternatively be `True`, indicating that
   the series has reached end-of-life but the date on which that happened is
   unknown.

``pyvinfo.is_eol(series)``
   Returns whether the given version series has reached end-of-life yet

``pyvinfo.is_released(version)``
   Returns whether the given version has been released yet.  For a major or
   minor version, this is the whether the first (in version order) micro
   version has been released.

``pyvinfo.is_supported(series)``
   Returns whether the given version series is currently supported (i.e., has
   at least one release out and is not yet end-of-life)

``pyvinfo.major_versions()``
   Returns a list in version order of all Python major versions that have ever
   been released

``pyinfo.micro_versions()``
   Returns a list in version order of all Python micro versions that have ever
   been released.  Versions in the form ``X.Y`` are included here as ``X.Y.0``.

``pyvinfo.minor_versions()``
   Returns a list in version order of all Python minor versions that have ever
   been released

``pyvinfo.release_date(version)``
   Returns the release date of the given Python version.  For a major or minor
   version, this is the release date of its first (in version order) micro
   version.  The return value may be `None`, indicating that, though the
   version has been released and is known to the database, its release date is
   unknown.

``pyvinfo.subversions(version)``
   Returns a list in version order of all released subversions of the given
   version.  If ``version`` is a major version, this is all of its released
   minor versions.  If ``version`` is a minor version, this is all of its
   released micro versions.

``pyvinfo.supported_series()``
   Returns a list in version order of all Python version series (i.e., minor
   versions like 3.5) that are currently supported (i.e., that have at least
   one released made and are not yet end-of-life)


Utilities
---------

``UnknownVersionError``
   Exception raised when ``PyVersionInfo`` is asked for information about a
   version that does not appear in its database.  Operations that result in an
   ``UnknownVersionError`` may succeed later as more Python versions are
   announced & released.

   The unknown version is stored in an ``UnknownVersionError`` instance's
   ``version`` attribute.

``get_pyversion_info(url=pyversion_info.DATA_URL, cache_dir=pyversion_info.CACHE_DIR)``
    Fetches the latest version release data from ``url`` and returns a new
    ``PyVersionInfo`` object.  The HTTP response is cached in ``cache_dir`` to
    speed up future requests (or ``cache_dir`` can be set to `None` to disable
    caching).


Restrictions
============

The database is generally only updated when an edit is made to a release
schedule PEP.  Occasionally, a deadline listed in a PEP is missed, but the PEP
is not updated for a couple days, and so for a brief period this library will
falsely report the given version as released.

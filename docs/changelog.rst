.. currentmodule:: pyversion_info

Changelog
=========

v1.2.3 (in development)
-----------------------
- Drop support for Python 3.7
- Support Python 3.13
- Exclude click v8.2.2 from dependencies due to breakage caused by
  <https://github.com/pallets/click/issues/3024>


v1.2.2 (2024-02-04)
-------------------
- Support platformdirs v4.0
- Migrated from setuptools to hatch
- Support cachecontrol v0.14


v1.2.1 (2023-11-09)
-------------------
- Support Python 3.12
- Correct the order of results returned by
  `PyPyVersionInfo.supported_cpython_series()`


v1.2.0 (2023-09-23)
-------------------
- Support platformdirs v3.0
- Update pydantic to v2.0


v1.1.1 (2023-06-01)
-------------------
- Support Python 3.11
- Support cachecontrol 0.13


v1.1.0 (2021-11-08)
-------------------
- Use pydantic internally for parsing & validating version databases
- `~CPythonVersionInfo.eol_date()` and `~CPythonVersionInfo.is_eol()` now
  accept major and micro versions


v1.0.0 (2021-11-04)
-------------------
- Support Python 3.10
- Drop support for Python 3.6
- Support for fetching information on PyPy versions has been added.  With it
  come the following changes:

  - The schema used by the database (and thus the URL for the default database)
    has been modified
  - ``PyVersionInfo`` has been renamed to `CPythonVersionInfo`
  - A new `PyPyVersionInfo` class has been added
  - A new `VersionDatabase` class has been added, containing a
    `CPythonVersionInfo` instance and a `PyPyVersionInfo` instance
  - ``get_pyversion_info()`` is now `VersionDatabase.fetch()`
  - The command-line interface now takes a ``--pypy`` option for showing
    details about PyPy versions

- The ``unreleased`` argument to `~VersionInfo.major_versions()`,
  `~VersionInfo.minor_versions()`, `~VersionInfo.micro_versions()`, and
  `~VersionInfo.subversions()` has been removed; the methods now return all
  known versions, released & unreleased
- `~VersionInfo.release_date()` now returns `None` for any known version whose
  release date is unknown, whether it's been released yet or not.  Use
  `~VersionInfo.is_released()` to determine whether such a version has been
  released.
- `~CPythonVersionInfo.eol_date()` now returns `None` for any known version
  whose EOL date is unknown, whether it's EOL yet or not.  Use
  `~CPythonVersionInfo.is_eol()` to determine whether such a version has
  reached end-of-life.
- Moved documentation from README file to a Read the Docs site


v0.4.0 (2021-10-03)
-------------------
- `~VersionInfo.major_versions()`, `~VersionInfo.minor_versions()`,
  `~VersionInfo.micro_versions()`, and `~VersionInfo.subversions()` now take
  optional ``unreleased`` arguments for including unreleased versions
- `~CPythonVersionInfo.is_supported()` now accepts major and micro versions
- `UnknownVersionError` now inherits `ValueError`
- Added a command-line interface


v0.3.0 (2021-10-01)
-------------------
- Add type annotations
- Switch from appdirs to platformdirs


v0.2.0 (2020-12-13)
-------------------
- Support Python 3.8 and 3.9
- Add a note to the README about the possibility of release deadlines being
  missed
- Drop support for Python 2.7, 3.4, and 3.5
- Properly close the ``requests`` session after downloading the database


v0.1.0 (2019-04-23)
-------------------
Initial release

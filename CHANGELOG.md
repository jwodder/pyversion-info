v1.1.0 (2021-11-08)
-------------------
- Use pydantic internally for parsing & validating version databases
- `eol_date()` and `is_eol()` now accept major and micro versions
- The `show` command now outputs the EOL date and EOL state for all CPython
  version levels

v1.0.0 (2021-11-04)
-------------------
- Support Python 3.10
- Drop support for Python 3.6
- Support for fetching information on PyPy versions has been added.  With it
  come the following changes:
    - The schema used by the database (and thus the URL for the default
      database) has been modified
    - `PyVersionInfo` has been renamed to `CPythonVersionInfo`
    - A new `PyPyVersionInfo` class has been added
    - A new `VersionDatabase` class has been added, containing a
      `CPythonVersionInfo` instance and a `PyPyVersionInfo` instance
    - `get_pyversion_info()` is now `VersionDatabase.fetch()`
    - The command-line interface now takes a `--pypy` option for showing
      details about PyPy versions
- The `unreleased` argument to `major_versions()`, `minor_versions()`,
  `micro_versions()`, and `subversions()` has been removed; the methods now
  return all known versions, released & unreleased
- `release_date()` now returns `None` for any known version whose release date
  is unknown, whether it's been released yet or not.  Use `is_released()` to
  determine whether such a version has been released.
- `eol_date()` now returns `None` for any known version whose EOL date is
  unknown, whether it's EOL yet or not.  Use `is_eol()` to determine whether
  such a version has reached end-of-life.
- Moved documentation from README file to a Read the Docs site

v0.4.0 (2021-10-03)
-------------------
- `major_versions()`, `minor_versions()`, `micro_versions()`, and
  `subversions()` now take optional `unreleased` arguments for including
  unreleased versions
- `is_supported()` now accepts major and micro versions
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
- Properly close the requests session after downloading the database

v0.1.0 (2019-04-23)
-------------------
Initial release

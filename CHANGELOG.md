v0.5.0 (in development)
-----------------------
- Support Python 3.10

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

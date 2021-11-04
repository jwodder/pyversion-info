.. currentmodule:: pyversion_info

API
===

Versions are passed to & returned from methods as strings in the form ``"X"``
(a major version), ``"X.Y"`` (a minor version), or ``"X.Y.Z"`` (a micro
version).

All dates are returned as `datetime.date` objects.

.. autoclass:: VersionDatabase()
    :exclude-members: fetch

    .. automethod:: fetch(url: str = DATA_URL, cache_dir: Union[str, pathlib.Path, None] = CACHE_DIR) -> pyversion_info.VersionDatabase
        :noindex:

.. autoclass:: VersionInfo()

.. autoclass:: CPythonVersionInfo()
    :show-inheritance:

.. autoclass:: PyPyVersionInfo()
    :show-inheritance:

.. autoexception:: UnknownVersionError
    :show-inheritance:

.. autodata:: DATA_URL
    :annotation:

.. autodata:: CACHE_DIR
    :annotation:

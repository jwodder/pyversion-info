"""
Get information about released & unreleased CPython and PyPy versions

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

Visit <https://github.com/jwodder/pyversion-info> or
<https://pyversion-info.rtfd.io> for more information.
"""

from __future__ import annotations

__version__ = "1.1.0"
__author__ = "John Thorvald Wodder II"
__author_email__ = "pyversion-info@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/pyversion-info"

from collections import OrderedDict
from dataclasses import dataclass
from datetime import date, datetime
import json
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Union
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from platformdirs import user_cache_dir
from pydantic import parse_obj_as
import requests
from .util import MajorVersion, MicroVersion, MinorVersion, RawDatabase

__all__ = [
    "CACHE_DIR",
    "CPythonVersionInfo",
    "DATA_URL",
    "PyPyVersionInfo",
    "UnknownVersionError",
    "VersionDatabase",
    "VersionInfo",
]

#: The default URL from which the version database is downloaded
DATA_URL = (
    "https://raw.githubusercontent.com/jwodder/pyversion-info-data/master"
    "/pyversion-info-data.v1.json"
)

#: The default directory in which the downloaded version database is cached
CACHE_DIR = user_cache_dir("pyversion-info", "jwodder")


@dataclass
class VersionDatabase:
    """
    .. versionadded:: 1.0.0

    A database of CPython and PyPy version information.  Instances are
    constructed from JSON objects following `this JSON Schema`__.

    __ https://raw.githubusercontent.com/jwodder/pyversion-info-data/master/
       pyversion-info-data.v1.schema.json
    """

    #: The date & time when the database was last updated
    last_modified: datetime
    #: A database of CPython version information
    cpython: CPythonVersionInfo
    #: A database of PyPy version information
    pypy: PyPyVersionInfo

    @classmethod
    def fetch(
        cls, url: str = DATA_URL, cache_dir: Union[str, Path, None] = CACHE_DIR
    ) -> VersionDatabase:
        """
        Fetches the latest version information from the JSON document at
        ``url`` and returns a new `VersionDatabase` instance

        :param str url: The URL from which to fetch the data
        :param Union[str,Path,None] cache_dir: The directory to use for caching
            HTTP requests.  May be `None` to disable caching.
        :rtype: VersionDatabase
        """
        s = requests.Session()
        if cache_dir is not None:
            s = CacheControl(s, cache=FileCache(cache_dir))
        with s:
            r = s.get(url)
            r.raise_for_status()
            return cls.parse_obj(r.json())

    @classmethod
    def parse_file(cls, filepath: Union[str, Path]) -> VersionDatabase:
        """
        Parses a version database from a JSON file and returns a new
        `VersionDatabase` instance
        """
        with open(filepath, "rb") as fp:
            return cls.parse_obj(json.load(fp))

    @classmethod
    def parse_obj(cls, data: dict) -> VersionDatabase:
        """
        Parses a version database from a `dict` deserialized from a JSON
        document and returns a new `VersionDatabase` instance
        """
        rawdb = RawDatabase.parse_obj(data)
        return cls(
            last_modified=rawdb.last_modified,
            cpython=CPythonVersionInfo(
                rawdb.cpython.release_dates, rawdb.cpython.eol_dates
            ),
            pypy=PyPyVersionInfo(rawdb.pypy.release_dates, rawdb.pypy.cpython_versions),
        )


class VersionInfo:
    """
    .. versionadded:: 1.0.0

    A base class for storing & querying versions and their release dates
    """

    def __init__(self, release_dates: Mapping[MicroVersion, Union[date, bool]]) -> None:
        self.release_dates: Dict[MicroVersion, Union[date, bool]] = dict(release_dates)
        self.version_trie: Dict[int, Dict[int, List[int]]] = OrderedDict()
        for v in sorted(release_dates.keys()):
            self.version_trie.setdefault(v.x, OrderedDict()).setdefault(v.y, []).append(
                v.z
            )

    def major_versions(self) -> List[str]:
        """
        Returns a list in version order of all known major versions (as
        strings).

        .. versionchanged:: 1.0.0
            Now returns all known versions, released & unreleased
        """
        return list(map(str, self.version_trie.keys()))

    def minor_versions(self) -> List[str]:
        """
        Returns a list in version order of all known minor versions

        .. versionchanged:: 1.0.0
            Now returns all known versions, released & unreleased
        """
        minors: List[str] = []
        for major, subtrie in self.version_trie.items():
            minors.extend(f"{major}.{minor}" for minor in subtrie.keys())
        return minors

    def micro_versions(self) -> List[str]:
        """
        Returns a list in version order of all known micro versions

        .. versionchanged:: 1.0.0
            Now returns all known versions, released & unreleased
        """
        micros: List[str] = []
        for major, subtrie in self.version_trie.items():
            for minor, sublist in subtrie.items():
                micros.extend(f"{major}.{minor}.{mc}" for mc in sublist)
        return micros

    def subversions(self, version: str) -> List[str]:
        """
        Returns a list in version order of all known subversions of the given
        version.  If ``version`` is a major version, this is all of its minor
        versions.  If ``version`` is a minor version, this is all of its micro
        versions.

        .. versionchanged:: 1.0.0
            Now returns all known subversions, released & unreleased

        :param str version: a major or minor version
        :raises UnknownVersionError: if there is no entry for ``version`` in
            the database
        :raises ValueError: if ``version`` is not a valid major or minor
            version string
        """
        v = parse_version(version)
        try:
            if isinstance(v, MajorVersion):
                subs = [f"{v.x}.{y}" for y in self.version_trie[v.x].keys()]
            elif isinstance(v, MinorVersion):
                subs = [f"{v.x}.{v.y}.{z}" for z in self.version_trie[v.x][v.y]]
            else:
                assert isinstance(v, MicroVersion)
                raise ValueError(f"Micro versions do not have subversions: {version!r}")
        except KeyError:
            raise UnknownVersionError(version)
        return subs

    def _release_date(self, version: str) -> Union[date, bool]:
        v = parse_version(version)
        try:
            if isinstance(v, MajorVersion):
                y, zs = next(iter(self.version_trie[v.x].items()))
                m = MicroVersion.construct(v.x, y, zs[0])
            elif isinstance(v, MinorVersion):
                m = MicroVersion.construct(v.x, v.y, self.version_trie[v.x][v.y][0])
            else:
                assert isinstance(v, MicroVersion)
                m = v
            return self.release_dates[m]
        except KeyError:
            raise UnknownVersionError(version)

    def release_date(self, version: str) -> Optional[date]:
        """
        Returns the release date of the given version.  For a major or minor
        version, this is the release date of its first (in version order) micro
        version.  The return value may be `None`, indicating that, though the
        version is known to the database, its release date is not; use
        `is_released()` to determine whether such a version has been released
        yet.

        .. versionchanged:: 1.0.0
            Unknown release dates are now always returned as `None`

        :param str version: the version to fetch the release date of
        :rtype: Optional[datetime.date]
        :raises UnknownVersionError: if there is no micro version corresponding
            to ``version`` in the database
        :raises ValueError: if ``version`` is not a valid version string
        """
        d = self._release_date(version)
        if isinstance(d, date):
            return d
        else:
            return None

    def is_released(self, version: str) -> bool:
        """
        Returns whether the given version has been released yet.  For a major
        or minor version, this is the whether the first (in version order)
        micro version has been released.

        :param str version: the version to query the release status of
        :rtype: bool
        :raises UnknownVersionError: if there is no micro version corresponding
            to ``version`` in the database
        :raises ValueError: if ``version`` is not a valid version string
        """
        d = self._release_date(version)
        if isinstance(d, date):
            return d <= date.today()
        else:
            return d


class CPythonVersionInfo(VersionInfo):
    """
    A class for storing & querying CPython versions, their release dates, and
    series EOL dates

    .. versionchanged:: 1.0.0
        This class was previously named ``PyVersionInfo``
    """

    def __init__(
        self,
        release_dates: Mapping[MicroVersion, Union[date, bool]],
        eol_dates: Mapping[MinorVersion, Union[date, bool]],
    ) -> None:
        super().__init__(release_dates)
        self.eol_dates: Dict[MinorVersion, Union[date, bool]] = dict(eol_dates)

    def supported_series(self) -> List[str]:
        """
        Returns a list in version order of all CPython version series (i.e.,
        minor versions like 3.5) that are currently supported (i.e., that have
        at least one release made and are not yet end-of-life)
        """
        return [
            v
            for v in self.minor_versions()
            if self.is_released(v) and not self.is_eol(v)
        ]

    def _eol_date(self, version: str) -> Union[date, bool]:
        v = parse_version(version)
        try:
            if isinstance(v, MajorVersion):
                subdates = [
                    self.eol_dates[MinorVersion.construct(v.x, y)]
                    for y in self.version_trie[v.x].keys()
                ]
                if all(
                    (isinstance(d, date) and d <= date.today()) or d is True
                    for d in subdates
                ):
                    return subdates[-1]
                else:
                    return False
            elif isinstance(v, MinorVersion):
                return self.eol_dates[v]
            else:
                assert isinstance(v, MicroVersion)
                return self.eol_dates[v.minor]
        except KeyError:
            raise UnknownVersionError(version)

    def eol_date(self, version: str) -> Optional[date]:
        """
        Returns the end-of-life date of the given CPython version.  The return
        value may be `None`, indicating that, though the version is known to
        the database, its EOL date is not; use `is_eol()` to determine whether
        such a version has reached end-of-life yet.

        For a major version, this method returns the EOL date of the last
        subversion **if** every subversion is already end-of-life; otherwise,
        it returns `None`.  For a micro version, this returns the EOL date of
        the corresponding minor version.

        .. versionchanged:: 1.0.0
            Unknown end-of-life dates are now always returned as `None`

        .. versionchanged:: 1.1.0
            Major and micro versions are now accepted

        :param str version: the version to fetch the end-of-life date of
        :rtype: Optional[datetime.date]
        :raises UnknownVersionError: if there is no entry for ``version`` in
            the end-of-life table
        :raises ValueError: if ``version`` is not a valid version string
        """
        d = self._eol_date(version)
        if isinstance(d, date):
            return d
        else:
            return None

    def is_eol(self, series: str) -> bool:
        """
        Returns whether the given version has reached end-of-life yet.  For a
        major version, this is whether every subversion has reached
        end-of-life.  For a micro version, this is whether the corresponding
        minor version has reached end-of-life.

        .. versionchanged:: 1.1.0
            Major and micro versions are now accepted

        :param str series: a Python version number
        :rtype: bool
        :raises UnknownVersionError: if there is no entry for ``version`` in
            the end-of-life table
        :raises ValueError: if ``version`` is not a valid version string
        """
        d = self._eol_date(series)
        if isinstance(d, date):
            return d <= date.today()
        else:
            return d

    def is_supported(self, version: str) -> bool:
        """
        Returns whether the given version is currently supported.  For a micro
        version, this is whether it has been released and the corresponding
        minor version is not yet end-of-life.  For a major or minor version,
        this is whether at least one subversion is supported.

        :param str version: the version to query the support status of
        :rtype: bool
        :raises UnknownVersionError: if there is no entry for ``version`` in
            the database
        """
        v = parse_version(version)
        if isinstance(v, MajorVersion):
            return any(map(self.is_supported, self.subversions(v)))
        elif isinstance(v, MinorVersion):
            return (not self.is_eol(v)) and any(
                map(self.is_released, self.subversions(v))
            )
        else:
            assert isinstance(v, MicroVersion)
            return (not self.is_eol(v.minor)) and self.is_released(version)


class PyPyVersionInfo(VersionInfo):
    """
    .. versionadded:: 1.0.0

    A class for storing & querying PyPy versions, their release dates, and
    their corresponding CPython versions
    """

    def __init__(
        self,
        release_dates: Mapping[MicroVersion, Union[date, bool]],
        cpython_versions: Mapping[MicroVersion, List[MicroVersion]],
    ) -> None:
        super().__init__(release_dates)
        self.cpython_versions: Dict[MicroVersion, List[MicroVersion]] = {
            v: sorted(versions) for v, versions in cpython_versions.items()
        }

    def supported_cpython(self, version: str) -> List[str]:
        """
        Given a PyPy micro version, returns a list of the corresponding CPython
        micro versions in version order.

        :raises UnknownVersionError: if there is no entry for ``version`` in
            the database
        :raises ValueError: if ``version`` is not a valid micro version string
        """
        try:
            v = MicroVersion.parse(version)
        except ValueError:
            raise ValueError(f"Invalid micro version: {version!r}")
        try:
            return list(self.cpython_versions[v])
        except KeyError:
            raise UnknownVersionError(version)

    def supported_cpython_series(
        self, version: str, released: bool = False
    ) -> List[str]:
        """
        Given a PyPy version, returns a list of all CPython series supported by
        that version or its subversions in version order.  If ``released`` is
        true, only released versions are considered.

        >>> db.supported_cpython_series("7.3.5")
        ['2.7', '3.7']
        >>> db.supported_cpython_series("7.3")
        ['2.7', '3.6', '3.7', '3.8']
        >>> db.supported_cpython_series("7")
        ['2.7', '3.5', '3.6', '3.7', '3.8']

        :raises UnknownVersionError: if there is no entry for ``version`` in
            the database
        :raises ValueError: if ``version`` is not a valid version string
        """
        v = parse_version(version)
        try:
            if isinstance(v, MajorVersion):
                micros = [
                    MicroVersion.construct(v.x, y, z)
                    for y, zs in self.version_trie[v.x].items()
                    for z in zs
                ]
            elif isinstance(v, MinorVersion):
                micros = [
                    MicroVersion.construct(v.x, v.y, z)
                    for z in self.version_trie[v.x][v.y]
                ]
            else:
                assert isinstance(v, MicroVersion)
                micros = [v]
            series_set = {
                str(cpyv.minor)
                for m in micros
                if not released or self.is_released(m)
                for cpyv in self.cpython_versions[m]
            }
            return sorted(series_set)
        except KeyError:
            raise UnknownVersionError(version)


class UnknownVersionError(ValueError):
    """
    Subclass of `ValueError` raised when a `VersionInfo` instance is asked for
    information about a version that does not appear in its database.
    Operations that result in an `UnknownVersionError` may succeed later as
    more Python versions are announced & released.
    """

    def __init__(self, version: str) -> None:
        #: The unknown version the caller asked about
        self.version = str(version)

    def __str__(self) -> str:
        return f"Unknown version: {self.version!r}"


def parse_version(s: str) -> Union[MajorVersion, MinorVersion, MicroVersion]:
    """
    Convert a version string of the form ``X``, ``X.Y``, or ``X.Y.Z`` to a
    `Version` instance

    :raises ValueError: if ``s`` is not a valid version string
    """
    try:
        # <https://github.com/python/mypy/issues/4625>
        v: Union[MajorVersion, MinorVersion, MicroVersion] = parse_obj_as(
            Union[MajorVersion, MinorVersion, MicroVersion], s  # type: ignore[arg-type]
        )
    except ValueError:
        raise ValueError(f"Invalid version string: {s!r}")
    return v

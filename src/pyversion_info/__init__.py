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

__version__ = "1.0.0"
__author__ = "John Thorvald Wodder II"
__author_email__ = "pyversion-info@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/pyversion-info"

from collections import OrderedDict
from dataclasses import dataclass
from datetime import date, datetime
import json
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple, Union
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from platformdirs import user_cache_dir
import requests

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
        return cls(
            last_modified=datetime.fromisoformat(data["last_modified"]),
            cpython=CPythonVersionInfo(
                data["cpython"]["release_dates"], data["cpython"]["eol_dates"]
            ),
            pypy=PyPyVersionInfo(
                data["pypy"]["release_dates"], data["pypy"]["cpython_versions"]
            ),
        )


class VersionInfo:
    """
    .. versionadded:: 1.0.0

    A base class for storing & querying versions and their release dates
    """

    def __init__(self, release_dates: Mapping[str, Union[str, bool]]) -> None:
        # `release_dates` must map X.Y.Z strings to ISO 8601 dates or booleans
        self.release_dates: Dict[str, Union[date, bool]] = {
            v: parse_date(d) for v, d in release_dates.items()
        }
        self.version_trie: Dict[int, Dict[int, List[int]]] = OrderedDict()
        for x, y, z in sorted(map(parse_version, release_dates.keys())):
            self.version_trie.setdefault(x, OrderedDict()).setdefault(y, []).append(z)

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
            minors.extend(unparse_version((major, minor)) for minor in subtrie.keys())
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
                micros.extend(unparse_version((major, minor, mc)) for mc in sublist)
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
            if len(v) == 1:
                subs = [
                    unparse_version(v + (y,)) for y in self.version_trie[v[0]].keys()
                ]
            elif len(v) == 2:
                subs = [
                    unparse_version(v + (z,)) for z in self.version_trie[v[0]][v[1]]
                ]
            else:
                assert len(v) == 3
                raise ValueError(f"Micro versions do not have subversions: {version!r}")
        except KeyError:
            raise UnknownVersionError(version)
        return subs

    def _release_date(self, version: str) -> Union[date, bool]:
        v = parse_version(version)
        try:
            if len(v) == 1:
                y, zs = next(iter(self.version_trie[v[0]].items()))
                v += (y, zs[0])
            elif len(v) == 2:
                v += (self.version_trie[v[0]][v[1]][0],)
            vstr = unparse_version(v)
            return self.release_dates[vstr]
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
        release_dates: Mapping[str, Union[str, bool]],
        eol_dates: Mapping[str, Union[str, bool]],
    ) -> None:
        super().__init__(release_dates)
        self.eol_dates: Dict[str, Union[date, bool]] = {
            v: parse_date(d) for v, d in eol_dates.items()
        }

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

    def _eol_date(self, series: str) -> Union[date, bool]:
        try:
            x, y = map(int, series.split("."))
        except ValueError:
            raise ValueError(f"Invalid series name: {series!r}")
        try:
            return self.eol_dates[f"{x}.{y}"]
        except KeyError:
            raise UnknownVersionError(series)

    def eol_date(self, series: str) -> Optional[date]:
        """
        Returns the end-of-life date of the given CPython version series (i.e.,
        a minor version like 3.5).  The return value may be `None`, indicating
        that, though the series is known to the database, its EOL date is not;
        use `is_eol()` to determine whether such a version has reached
        end-of-life yet.

        .. versionchanged:: 1.0.0
            Unknown end-of-life dates are now always returned as `None`

        :param str series: a Python version series/minor version number
        :rtype: Optional[datetime.date]
        :raises UnknownVersionError: if there is no entry for ``series`` in the
            end-of-life table
        :raises ValueError: if ``series`` is not a valid minor version string
        """
        d = self._eol_date(series)
        if isinstance(d, date):
            return d
        else:
            return None

    def is_eol(self, series: str) -> bool:
        """
        Returns whether the given version series has reached end-of-life yet

        :param str series: a Python version series/minor version number
        :rtype: bool
        :raises UnknownVersionError: if there is no entry for ``series`` in the
            end-of-life table
        :raises ValueError: if ``series`` is not a valid minor version string
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
        if len(v) == 1:
            return any(map(self.is_supported, self.subversions(version)))
        elif len(v) == 2:
            return (not self.is_eol(version)) and any(
                map(self.is_released, self.subversions(version))
            )
        else:
            x, y, _ = v
            return (not self.is_eol(unparse_version((x, y)))) and self.is_released(
                version
            )


class PyPyVersionInfo(VersionInfo):
    """
    .. versionadded:: 1.0.0

    A class for storing & querying PyPy versions, their release dates, and
    their corresponding CPython versions
    """

    def __init__(
        self,
        release_dates: Mapping[str, Union[str, bool]],
        cpython_versions: Mapping[str, List[str]],
    ) -> None:
        super().__init__(release_dates)
        self.cpython_versions: Dict[str, List[str]] = {
            v: sorted(versions, key=parse_version)
            for v, versions in cpython_versions.items()
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
            x, y, z = map(int, version.split("."))
        except ValueError:
            raise ValueError(f"Invalid micro version: {version!r}")
        try:
            return list(self.cpython_versions[f"{x}.{y}.{z}"])
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
            if len(v) == 1:
                (x,) = v
                micros = [
                    f"{x}.{y}.{z}" for y, zs in self.version_trie[x].items() for z in zs
                ]
            elif len(v) == 2:
                x, y = v
                micros = [f"{x}.{y}.{z}" for z in self.version_trie[x][y]]
            else:
                micros = [unparse_version(v)]
            series_set = {
                parse_version(cpyv)[:2]
                for m in micros
                if not released or self.is_released(m)
                for cpyv in self.cpython_versions[m]
            }
            return list(map(unparse_version, sorted(series_set)))
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
        self.version = version

    def __str__(self) -> str:
        return f"Unknown version: {self.version!r}"


def parse_date(s: Union[str, bool]) -> Union[date, bool]:
    """
    Convert a string of the form ``YYYY-MM-DD`` into a `datetime.date` object.
    Booleans are passed through unaltered.
    """
    if isinstance(s, bool):
        return s
    else:
        return date.fromisoformat(s)


def parse_version(s: str) -> Tuple[int, ...]:
    """
    Convert a version string of the form ``X``, ``X.Y``, or ``X.Y.Z`` to a
    tuple of integers

    :raises ValueError: if ``s`` is not a valid version string
    """
    try:
        v = tuple(map(int, s.split(".")))
    except ValueError:
        raise ValueError(f"Invalid version string: {s!r}")
    if len(v) < 1 or len(v) > 3:
        raise ValueError(f"Invalid version string: {s!r}")
    return v


def unparse_version(v: Iterable[int]) -> str:
    """Convert a sequence of integers to a dot-separated string"""
    return ".".join(map(str, v))

"""
List released Python versions and their release & EOL dates

Ever needed to know what Python versions were currently supported, or how many
subversions a given Python version had?  Wondering how long until a given
version came out or reached end-of-life?  The answers to these and some other
questions can be found with this library.

``pyversion-info`` pulls its data every run from
`jwodder/pyversion-info-data <https://github.com/jwodder/pyversion-info-data>`_
on GitHub.  Prerelease versions are not (currently) included.  I promise
24-hour turnaround times for keeping the database up-to-date until I am hit by
a bus.

Visit <https://github.com/jwodder/pyversion-info> for more information.
"""

__version__ = "0.4.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "pyversion-info@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/pyversion-info"

from collections import OrderedDict
from datetime import date, datetime
from enum import Enum
import sys
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Tuple, Union
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from platformdirs import user_cache_dir
import requests

__all__ = [
    "PyVersionInfo",
    "UnknownVersionError",
    "get_pyversion_info",
]

#: The default URL from which to download the version release data
DATA_URL = (
    "https://raw.githubusercontent.com/jwodder/pyversion-info-data/master"
    "/pyversion-info-data.json"
)

#: The default directory in which the version release data is cached
CACHE_DIR = user_cache_dir("pyversion-info", "jwodder")

if TYPE_CHECKING:
    if sys.version_info[:2] >= (3, 8):
        from typing import Literal, TypedDict
    else:
        from typing_extensions import Literal, TypedDict

    TRUE = Literal[True]

    class PyVersionInfoData(TypedDict):
        version_release_dates: Dict[str, Optional[str]]
        series_eol_dates: Dict[str, Union[None, TRUE, str]]


class UndatedEOL(Enum):
    NOT_EOL = 1
    IS_EOL = 2


def get_pyversion_info(
    url: str = DATA_URL, cache_dir: Optional[str] = CACHE_DIR
) -> "PyVersionInfo":
    """
    Fetches the latest version release data from ``url`` and returns a new
    `PyVersionInfo` object

    :param str url: The URL from which to fetch the data
    :param str cache_dir: The directory to use for caching HTTP requests.  May
        be `None` to disable caching.
    :rtype: PyVersionInfo
    """
    s = requests.Session()
    if cache_dir is not None:
        s = CacheControl(s, cache=FileCache(cache_dir))
    with s:
        r = s.get(url)
        r.raise_for_status()
        return PyVersionInfo(r.json())


class PyVersionInfo:
    """A class for querying Python versions and their release & EOL dates"""

    def __init__(self, data: "PyVersionInfoData") -> None:
        """
        :param dict data: Version release dates and series EOL dates structured
            in accordance with `this JSON Schema`__

        __ https://raw.githubusercontent.com/jwodder/pyversion-info-data/
           master/pyversion-info-data.schema.json
        """
        self.version_release_dates: Dict[str, Optional[date]] = {
            v: parse_release_date(d) for v, d in data["version_release_dates"].items()
        }
        self.series_eol_dates: Dict[str, Union[date, UndatedEOL]] = {
            v: parse_eol_date(d) for v, d in data["series_eol_dates"].items()
        }
        self.version_trie: Dict[int, Dict[int, List[int]]] = OrderedDict()
        for v in sorted(map(parse_version, self.version_release_dates.keys())):
            x, y, z = v
            self.version_trie.setdefault(x, OrderedDict()).setdefault(y, []).append(z)

    def supported_series(self) -> List[str]:
        """
        Returns a list in version order of all Python version series (i.e.,
        minor versions like 3.5) that are currently supported (i.e., that have
        at least one release made and are not yet end-of-life)

        :rtype: list[str]
        """
        return [v for v in self.minor_versions() if not self.is_eol(v)]

    def major_versions(self, unreleased: bool = False) -> List[str]:
        """
        Returns a list in version order of all Python major versions (as
        strings).  If ``unreleased`` is true (default: `False`), the list
        includes unreleased versions; otherwise, they are omitted.

        .. versionchanged:: 0.4.0
            ``unreleased`` argument added

        :param bool unreleased: whether to include unreleased versions
        :rtype: list[str]
        """
        return [
            str(v)
            for v in self.version_trie.keys()
            if unreleased or self.is_released(str(v))
        ]

    def minor_versions(self, unreleased: bool = False) -> List[str]:
        """
        Returns a list in version order of all Python minor versions.  If
        ``unreleased`` is true (default: `False`), the list includes unreleased
        versions; otherwise, they are omitted.

        .. versionchanged:: 0.4.0
            ``unreleased`` argument added

        :param bool unreleased: whether to include unreleased versions
        :rtype: list[str]
        """
        minors: List[str] = []
        for major, subtrie in self.version_trie.items():
            minors.extend(unparse_version((major, minor)) for minor in subtrie.keys())
        if unreleased:
            return minors
        else:
            return list(filter(self.is_released, minors))

    def micro_versions(self, unreleased: bool = False) -> List[str]:
        """
        Returns a list in version order of all Python micro versions
        Versions in the form ``X.Y`` are included here as ``X.Y.0``.

        If ``unreleased`` is true (default: `False`), the list includes
        unreleased versions; otherwise, they are omitted.

        .. versionchanged:: 0.4.0
            ``unreleased`` argument added

        :param bool unreleased: whether to include unreleased versions
        :rtype: list[str]
        """
        micros: List[str] = []
        for major, subtrie in self.version_trie.items():
            for minor, sublist in subtrie.items():
                micros.extend(unparse_version((major, minor, mc)) for mc in sublist)
        if unreleased:
            return micros
        else:
            return list(filter(self.is_released, micros))

    def release_date(self, version: str) -> Optional[date]:
        """
        Returns the release date of the given Python version.  For a major or
        minor version, this is the release date of its first (in version order)
        micro version.  The return value may be `None`, indicating that, though
        the version has been released and is known to the database, its release
        date is unknown.

        :param str version: the version to fetch the release date of
        :rtype: datetime.date
        :raises UnknownVersionError: if there is no micro version corresponding
            to ``version`` in the database
        :raises ValueError: if ``version`` is not a valid version string
        """
        v = parse_version(version)
        try:
            if len(v) == 1:
                y, zs = next(iter(self.version_trie[v[0]].items()))
                v += (y, zs[0])
            elif len(v) == 2:
                v += (self.version_trie[v[0]][v[1]][0],)
            vstr = unparse_version(v)
            return self.version_release_dates[vstr]
        except KeyError:
            raise UnknownVersionError(version)

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
        d = self.release_date(version)
        return d is None or d <= date.today()

    def eol_date(self, series: str) -> "Union[None, TRUE, date]":
        """
        Returns the end-of-life date of the given Python version series (i.e.,
        a minor version like 3.5).  The return value may be `None`, indicating
        that the series is not yet end-of-life and its end-of-life date is
        unknown or undetermined.  The return value may alternatively be `True`,
        indicating that the series has reached end-of-life but the date on
        which that happened is unknown.

        :param str series: a Python version series/minor version number
        :rtype: datetime.date
        :raises UnknownVersionError: if there is no entry for ``series`` in the
            end-of-life table
        :raises ValueError: if ``series`` is not a valid minor version string
        """
        try:
            x, y = map(int, series.split("."))
        except ValueError:
            raise ValueError(f"Invalid series name: {series!r}")
        try:
            return from_eol_date(self.series_eol_dates[f"{x}.{y}"])
        except KeyError:
            raise UnknownVersionError(series)

    def is_eol(self, series: str) -> bool:
        """
        Returns whether the given version series has reached end-of-life yet

        :param str series: a Python version series/minor version number
        :rtype: bool
        :raises UnknownVersionError: if there is no entry for ``series`` in the
            end-of-life table
        :raises ValueError: if ``series`` is not a valid minor version string
        """
        d = self.eol_date(series)
        return d is not None and (d is True or d <= date.today())

    def is_supported(self, version: str) -> bool:
        """
        Returns whether the given version is currently supported.  For a micro
        version, this is whether it has been released and the corresponding
        minor version is not yet end-of-life.  For a major or minor version,
        this is whether at least one subversion is supported.

        .. versionchanged:: 0.4.0
            Major and micro versions now accepted

        :param str version: the version to query the support status of
        :rtype: bool
        :raises UnknownVersionError: if there is no entry for ``version`` in
            the database
        """
        v = parse_version(version)
        if len(v) == 1:
            return not all(map(self.is_eol, self.subversions(version)))
        elif len(v) == 2:
            return (not self.is_eol(version)) and bool(self.subversions(version))
        else:
            x, y, _ = v
            return (not self.is_eol(unparse_version((x, y)))) and self.is_released(
                version
            )

    def subversions(self, version: str, unreleased: bool = False) -> List[str]:
        """
        Returns a list in version order of all subversions of the given
        version.  If ``version`` is a major version, this is all of its
        released minor versions.  If ``version`` is a minor version, this is
        all of its released micro versions.

        If ``unreleased`` is true (default: `False`), the list includes
        unreleased subversions.  Otherwise, they are omitted.

        .. versionchanged:: 0.4.0
            ``unreleased`` argument added

        :param str version: a Python major or minor version
        :param bool unreleased: whether to include unreleased subversions
        :rtype: list[str]
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
            elif len(v) == 3:
                raise ValueError(f"Micro versions do not have subversions: {version!r}")
        except KeyError:
            raise UnknownVersionError(version)
        if unreleased:
            return subs
        else:
            return list(filter(self.is_released, subs))


class UnknownVersionError(ValueError):
    """
    Subclass of `ValueError` raised when `PyVersionInfo` is asked for
    information about a version that does not appear in its database.
    Operations that result in an `UnknownVersionError` may succeed later as
    more Python versions are announced & released.
    """

    def __init__(self, version: str) -> None:
        #: The unknown version the caller asked about
        self.version = version

    def __str__(self) -> str:
        return f"Unknown version: {self.version!r}"


def parse_date(s: Union[str, bool, None]) -> Union[date, bool, None]:
    """
    Convert a string of the form ``YYYY-MM-DD`` into a `datetime.date` object.
    `None` values and booleans are passed through unaltered.
    """
    if s is None or isinstance(s, bool):
        return s
    else:
        return datetime.strptime(s, "%Y-%m-%d").date()


def parse_release_date(s: Union[str, bool, None]) -> Optional[date]:
    d = parse_date(s)
    if isinstance(d, date) or d is None:
        return d
    else:
        raise ValueError(f"Invalid release date: {s!r}")


def parse_eol_date(s: Union[str, bool, None]) -> Union[date, UndatedEOL]:
    d = parse_date(s)
    if isinstance(d, date):
        return d
    elif d:
        return UndatedEOL.IS_EOL
    else:
        return UndatedEOL.NOT_EOL


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


def from_eol_date(d: Union[date, UndatedEOL]) -> "Union[date, None, TRUE]":
    if isinstance(d, date):
        return d
    elif d is UndatedEOL.IS_EOL:
        return True
    else:
        assert d is UndatedEOL.NOT_EOL
        return None

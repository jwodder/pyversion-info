"""
Fetch supported Python versions, release dates, and EOL dates

Visit <https://github.com/jwodder/pyversion-info> for more information.
"""

__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'pyversion-info@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/pyversion-info'

from   collections                    import OrderedDict
from   datetime                       import date, datetime
from   appdirs                        import user_cache_dir
from   cachecontrol                   import CacheControl
from   cachecontrol.caches.file_cache import FileCache
import requests

__all__ = [
    'PyVersionInfo',
    'UnknownVersionError',
    'get_pyversion_info',
]

DATA_URL = 'https://raw.githubusercontent.com/jwodder/pyversion-info-data/master/pyversion-info-data.json'

CACHE_DIR = user_cache_dir('pyversion-info', 'jwodder')

def get_pyversion_info(url=DATA_URL, cache_dir=CACHE_DIR):
    s = requests.Session()
    if cache_dir is not None:
        s = CacheControl(s, cache=FileCache(cache_dir))
    r = s.get(url)
    r.raise_for_status()
    return PyVersionInfo(r.json())

class PyVersionInfo(object):
    def __init__(self, data):
        self.version_release_dates = {
            v: parse_date(d) for v,d in data["version_release_dates"].items()
        }
        self.series_eol_dates = {
            v: parse_date(d) for v,d in data["series_eol_dates"].items()
        }
        self.version_trie = OrderedDict()
        for v in sorted(map(parse_version, self.version_release_dates.keys())):
            x, y, z = v
            self.version_trie.setdefault(x, OrderedDict())\
                             .setdefault(y, [])\
                             .append(z)

    def supported_series(self):
        return [v for v in self.minor_versions() if self.is_supported(v)]

    def major_versions(self):
        return [
            str(v) for v in self.version_trie.keys() if self.is_released(str(v))
        ]

    def minor_versions(self):
        minors = []
        for major, subtrie in self.version_trie.items():
            minors.extend(
                unparse_version((major, minor)) for minor in subtrie.keys()
            )
        return [v for v in minors if self.is_released(v)]

    def micro_versions(self):
        micros = []
        for major, subtrie in self.version_trie.items():
            for minor, sublist in subtrie.items():
                micros.extend(
                    unparse_version((major, minor, mc)) for mc in sublist
                )
        return [v for v in micros if self.is_released(v)]

    def release_date(self, version):
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

    def is_released(self, version):
        d = self.release_date(version)
        return d is None or d <= date.today()

    def eol_date(self, series):
        try:
            x, y = map(int, series.split('.'))
        except ValueError:
            raise ValueError('Invalid series name: ' + repr(series))
        try:
            return self.series_eol_dates['{}.{}'.format(x,y)]
        except KeyError:
            raise UnknownVersionError(series)

    def is_eol(self, series):
        d = self.eol_date(series)
        return d and (d is True or d <= date.today())

    def is_supported(self, series):
        # Test is_eol() first so that invalid versions will be reported as
        # invalid series
        return (not self.is_eol(series)) and self.is_released(series)

    def subversions(self, version):
        v = parse_version(version)
        try:
            if len(v) == 1:
                subs = [
                    unparse_version(v + (y,))
                    for y in self.version_trie[v[0]].keys()
                ]
            elif len(v) == 2:
                subs = [
                    unparse_version(v + (z,))
                    for z in self.version_trie[v[0]][v[1]]
                ]
            elif len(v) == 3:
                raise ValueError(
                    'Micro versions do not have subversions: '+repr(version)
                )
        except KeyError:
            raise UnknownVersionError(version)
        return [s for s in subs if self.is_released(s)]


class UnknownVersionError(Exception):
    def __init__(self, version):
        self.version = version
        super(UnknownVersionError, self).__init__(version)

    def __str__(self):
        return 'Unknown version: ' + repr(self.version)


def parse_date(s):
    if s is None or isinstance(s, bool):
        return s
    else:
        return datetime.strptime(s, '%Y-%m-%d').date()

def parse_version(s):
    try:
        v = tuple(map(int, s.split('.')))
    except ValueError:
        raise ValueError('Invalid version string: ' + repr(s))
    if len(v) < 1 or len(v) > 3:
        raise ValueError('Invalid version string: ' + repr(s))
    return v

def unparse_version(v):
    return '.'.join(map(str, v))

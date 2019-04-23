from   appdirs                        import user_cache_dir
from   cachecontrol                   import CacheControl
from   cachecontrol.caches.file_cache import FileCache
import requests

PYVERSION_INFO_DATA_URL = 'https://raw.githubusercontent.com/jwodder/pyversion-info-data/master/pyversion-info-data.json'

CACHE_DIR = user_cache_dir('pyversion-info', 'jwodder')

def get_pyversion_info(url=PYVERSION_INFO_DATA_URL, cache_dir=CACHE_DIR):
    s = requests.Session()
    if cache_dir is not None:
        s = CacheControl(s, cache=FileCache(cache_dir))
    r = s.get(url)
    r.raise_for_status()
    return PyVersionInfo(r.json())

class PyVersionInfo(object):
    def __init__(self, data):
        raise NotImplementedError

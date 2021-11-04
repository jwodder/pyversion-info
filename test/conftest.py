import json
from pathlib import Path
import pytest
from pyversion_info import VersionDatabase

DATA_FILE = Path(__file__).with_name("data") / "pyversion-info-data.json"


@pytest.fixture(scope="session")
def version_database() -> VersionDatabase:
    with DATA_FILE.open() as fp:
        data = json.load(fp)
    return VersionDatabase.parse_obj(data)

from pathlib import Path
import pytest
from pyversion_info import VersionDatabase

DATA_FILE = Path(__file__).with_name("data") / "pyversion-info-data.json"


@pytest.fixture(scope="session")
def version_database() -> VersionDatabase:
    return VersionDatabase.parse_file(DATA_FILE)

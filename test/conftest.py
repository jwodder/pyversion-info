import json
from pathlib import Path
import pytest
from pytest_mock import MockerFixture
from pyversion_info import VersionDatabase

DATA_FILE = Path(__file__).with_name("data") / "pyversion-info-data.json"


@pytest.fixture(autouse=True)
def use_fixed_date(mocker: MockerFixture) -> None:
    # Mocking/monkeypatching just the `today()` method of `date` doesn't seem
    # to be an option, and monkeypatching the `date` class with a custom class
    # that just implements `today()` causes problems on PyPy.  Fortunately,
    # both CPython and PyPy implement `date.today()` by calling `time.time()`,
    # so we just need to mock that and hope the implementation never changes.
    mocker.patch("time.time", return_value=1556052408)
    # Time is now 2019-04-23T16:46:48-04:00.


@pytest.fixture(scope="session")
def version_database() -> VersionDatabase:
    with DATA_FILE.open() as fp:
        data = json.load(fp)
    return VersionDatabase.from_json_dict(data)

import json
from pathlib import Path
from traceback import format_exception
from typing import List
import click
from click.testing import CliRunner, Result
import pytest
from pytest_mock import MockerFixture
from pyversion_info.__main__ import main

DATA_FILE = str(Path(__file__).with_name("data") / "pyversion-info-data.json")


@pytest.fixture(autouse=True)
def use_fixed_date(mocker: MockerFixture) -> None:
    # Mocking/monkeypatching just the `today()` method of `date` doesn't seem
    # to be an option, and monkeypatching the `date` class with a custom class
    # that just implements `today()` causes problems on PyPy.  Fortunately,
    # both CPython and PyPy implement `date.today()` by calling `time.time()`,
    # so we just need to mock that and hope the implementation never changes.
    mocker.patch("time.time", return_value=1556052408)
    # Time is now 2019-04-23T16:46:48-04:00.


def show_result(r: Result) -> str:
    if r.exception is not None:
        assert isinstance(r.exc_info, tuple)
        return "".join(format_exception(*r.exc_info))
    else:
        return r.output


@pytest.mark.parametrize(
    "mode,versions",
    [
        ("--all", ["0", "1", "2", "3", "4"]),
        ("--not-eol", ["2", "3", "4"]),
        ("--released", ["0", "1", "2", "3"]),
        ("--supported", ["2", "3"]),
    ],
)
def test_cmd_list_major(mode: str, versions: List[str]) -> None:
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", mode, "major"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == "".join(v + "\n" for v in versions)
    if mode == "--released":
        r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "major"])
        assert r.exit_code == 0, show_result(r)
        assert r.output == "".join(v + "\n" for v in versions)


@pytest.mark.parametrize(
    "mode,versions",
    [
        (
            "--all",
            [
                "0.9",
                "1.0",
                "1.1",
                "1.2",
                "1.3",
                "1.4",
                "1.5",
                "1.6",
                "2.0",
                "2.1",
                "2.2",
                "2.3",
                "2.4",
                "2.5",
                "2.6",
                "2.7",
                "3.0",
                "3.1",
                "3.2",
                "3.3",
                "3.4",
                "3.5",
                "3.6",
                "3.7",
                "3.8",
                "4.0",
            ],
        ),
        ("--not-eol", ["2.7", "3.5", "3.6", "3.7", "3.8", "4.0"]),
        (
            "--released",
            [
                "0.9",
                "1.0",
                "1.1",
                "1.2",
                "1.3",
                "1.4",
                "1.5",
                "1.6",
                "2.0",
                "2.1",
                "2.2",
                "2.3",
                "2.4",
                "2.5",
                "2.6",
                "2.7",
                "3.0",
                "3.1",
                "3.2",
                "3.3",
                "3.4",
                "3.5",
                "3.6",
                "3.7",
            ],
        ),
        ("--supported", ["2.7", "3.5", "3.6", "3.7"]),
    ],
)
def test_cmd_list_minor(mode: str, versions: List[str]) -> None:
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", mode, "minor"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == "".join(v + "\n" for v in versions)
    if mode == "--released":
        r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "minor"])
        assert r.exit_code == 0, show_result(r)
        assert r.output == "".join(v + "\n" for v in versions)


@pytest.mark.parametrize(
    "mode,versions",
    [
        (
            "--all",
            [
                "0.9.0",
                "0.9.1",
                "0.9.2",
                "0.9.4",
                "0.9.5",
                "0.9.6",
                "0.9.8",
                "0.9.9",
                "1.0.0",
                "1.0.1",
                "1.0.2",
                "1.0.3",
                "1.0.4",
                "1.1.0",
                "1.1.1",
                "1.2.0",
                "1.3.0",
                "1.4.0",
                "1.5.0",
                "1.5.1",
                "1.5.2",
                "1.6.0",
                "1.6.1",
                "2.0.0",
                "2.0.1",
                "2.1.0",
                "2.1.1",
                "2.1.2",
                "2.1.3",
                "2.2.0",
                "2.2.1",
                "2.2.2",
                "2.2.3",
                "2.3.0",
                "2.3.1",
                "2.3.2",
                "2.3.3",
                "2.3.4",
                "2.3.5",
                "2.3.6",
                "2.3.7",
                "2.4.0",
                "2.4.1",
                "2.4.2",
                "2.4.3",
                "2.4.4",
                "2.4.5",
                "2.4.6",
                "2.5.0",
                "2.5.1",
                "2.5.2",
                "2.5.3",
                "2.5.4",
                "2.5.5",
                "2.5.6",
                "2.6.0",
                "2.6.1",
                "2.6.2",
                "2.6.3",
                "2.6.4",
                "2.6.5",
                "2.6.6",
                "2.6.7",
                "2.6.8",
                "2.6.9",
                "2.7.0",
                "2.7.1",
                "2.7.2",
                "2.7.3",
                "2.7.4",
                "2.7.5",
                "2.7.6",
                "2.7.7",
                "2.7.8",
                "2.7.9",
                "2.7.10",
                "2.7.11",
                "2.7.12",
                "2.7.13",
                "2.7.14",
                "2.7.15",
                "2.7.16",
                "2.7.17",
                "2.7.18",
                "3.0.0",
                "3.0.1",
                "3.1.0",
                "3.1.1",
                "3.1.2",
                "3.1.3",
                "3.1.4",
                "3.1.5",
                "3.2.0",
                "3.2.1",
                "3.2.2",
                "3.2.3",
                "3.2.4",
                "3.2.5",
                "3.2.6",
                "3.3.0",
                "3.3.1",
                "3.3.2",
                "3.3.3",
                "3.3.4",
                "3.3.5",
                "3.3.6",
                "3.3.7",
                "3.4.0",
                "3.4.1",
                "3.4.2",
                "3.4.3",
                "3.4.4",
                "3.4.5",
                "3.4.6",
                "3.4.7",
                "3.4.8",
                "3.4.9",
                "3.4.10",
                "3.5.0",
                "3.5.1",
                "3.5.2",
                "3.5.3",
                "3.5.4",
                "3.5.5",
                "3.5.6",
                "3.5.7",
                "3.6.0",
                "3.6.1",
                "3.6.2",
                "3.6.3",
                "3.6.4",
                "3.6.5",
                "3.6.6",
                "3.6.7",
                "3.6.8",
                "3.7.0",
                "3.7.1",
                "3.7.2",
                "3.7.3",
                "3.7.4",
                "3.8.0",
                "4.0.0",
            ],
        ),
        (
            "--not-eol",
            [
                "2.7.0",
                "2.7.1",
                "2.7.2",
                "2.7.3",
                "2.7.4",
                "2.7.5",
                "2.7.6",
                "2.7.7",
                "2.7.8",
                "2.7.9",
                "2.7.10",
                "2.7.11",
                "2.7.12",
                "2.7.13",
                "2.7.14",
                "2.7.15",
                "2.7.16",
                "2.7.17",
                "2.7.18",
                "3.5.0",
                "3.5.1",
                "3.5.2",
                "3.5.3",
                "3.5.4",
                "3.5.5",
                "3.5.6",
                "3.5.7",
                "3.6.0",
                "3.6.1",
                "3.6.2",
                "3.6.3",
                "3.6.4",
                "3.6.5",
                "3.6.6",
                "3.6.7",
                "3.6.8",
                "3.7.0",
                "3.7.1",
                "3.7.2",
                "3.7.3",
                "3.7.4",
                "3.8.0",
                "4.0.0",
            ],
        ),
        (
            "--released",
            [
                "0.9.0",
                "0.9.1",
                "0.9.2",
                "0.9.4",
                "0.9.5",
                "0.9.6",
                "0.9.8",
                "0.9.9",
                "1.0.0",
                "1.0.1",
                "1.0.2",
                "1.0.3",
                "1.0.4",
                "1.1.0",
                "1.1.1",
                "1.2.0",
                "1.3.0",
                "1.4.0",
                "1.5.0",
                "1.5.1",
                "1.5.2",
                "1.6.0",
                "1.6.1",
                "2.0.0",
                "2.0.1",
                "2.1.0",
                "2.1.1",
                "2.1.2",
                "2.1.3",
                "2.2.0",
                "2.2.1",
                "2.2.2",
                "2.2.3",
                "2.3.0",
                "2.3.1",
                "2.3.2",
                "2.3.3",
                "2.3.4",
                "2.3.5",
                "2.3.6",
                "2.3.7",
                "2.4.0",
                "2.4.1",
                "2.4.2",
                "2.4.3",
                "2.4.4",
                "2.4.5",
                "2.4.6",
                "2.5.0",
                "2.5.1",
                "2.5.2",
                "2.5.3",
                "2.5.4",
                "2.5.5",
                "2.5.6",
                "2.6.0",
                "2.6.1",
                "2.6.2",
                "2.6.3",
                "2.6.4",
                "2.6.5",
                "2.6.6",
                "2.6.7",
                "2.6.8",
                "2.6.9",
                "2.7.0",
                "2.7.1",
                "2.7.2",
                "2.7.3",
                "2.7.4",
                "2.7.5",
                "2.7.6",
                "2.7.7",
                "2.7.8",
                "2.7.9",
                "2.7.10",
                "2.7.11",
                "2.7.12",
                "2.7.13",
                "2.7.14",
                "2.7.15",
                "2.7.16",
                "3.0.0",
                "3.0.1",
                "3.1.0",
                "3.1.1",
                "3.1.2",
                "3.1.3",
                "3.1.4",
                "3.1.5",
                "3.2.0",
                "3.2.1",
                "3.2.2",
                "3.2.3",
                "3.2.4",
                "3.2.5",
                "3.2.6",
                "3.3.0",
                "3.3.1",
                "3.3.2",
                "3.3.3",
                "3.3.4",
                "3.3.5",
                "3.3.6",
                "3.3.7",
                "3.4.0",
                "3.4.1",
                "3.4.2",
                "3.4.3",
                "3.4.4",
                "3.4.5",
                "3.4.6",
                "3.4.7",
                "3.4.8",
                "3.4.9",
                "3.4.10",
                "3.5.0",
                "3.5.1",
                "3.5.2",
                "3.5.3",
                "3.5.4",
                "3.5.5",
                "3.5.6",
                "3.5.7",
                "3.6.0",
                "3.6.1",
                "3.6.2",
                "3.6.3",
                "3.6.4",
                "3.6.5",
                "3.6.6",
                "3.6.7",
                "3.6.8",
                "3.7.0",
                "3.7.1",
                "3.7.2",
                "3.7.3",
            ],
        ),
        (
            "--supported",
            [
                "2.7.0",
                "2.7.1",
                "2.7.2",
                "2.7.3",
                "2.7.4",
                "2.7.5",
                "2.7.6",
                "2.7.7",
                "2.7.8",
                "2.7.9",
                "2.7.10",
                "2.7.11",
                "2.7.12",
                "2.7.13",
                "2.7.14",
                "2.7.15",
                "2.7.16",
                "3.5.0",
                "3.5.1",
                "3.5.2",
                "3.5.3",
                "3.5.4",
                "3.5.5",
                "3.5.6",
                "3.5.7",
                "3.6.0",
                "3.6.1",
                "3.6.2",
                "3.6.3",
                "3.6.4",
                "3.6.5",
                "3.6.6",
                "3.6.7",
                "3.6.8",
                "3.7.0",
                "3.7.1",
                "3.7.2",
                "3.7.3",
            ],
        ),
    ],
)
def test_cmd_list_micro(mode: str, versions: List[str]) -> None:
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", mode, "micro"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == "".join(v + "\n" for v in versions)
    if mode == "--released":
        r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "micro"])
        assert r.exit_code == 0, show_result(r)
        assert r.output == "".join(v + "\n" for v in versions)


@pytest.mark.parametrize(
    "version,subversions,data,headers",
    [
        (
            "1",
            "released",
            {
                "version": "1",
                "level": "major",
                "release_date": "1994-01-26",
                "is_released": True,
                "is_supported": False,
                "eol_date": None,
                "is_eol": True,
                "subversions": ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"],
            },
            (
                "Version: 1\n"
                "Level: major\n"
                "Release-Date: 1994-01-26\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: yes\n"
                "Subversions: 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6\n"
            ),
        ),
        (
            "1",
            "all",
            {
                "version": "1",
                "level": "major",
                "release_date": "1994-01-26",
                "is_released": True,
                "is_supported": False,
                "eol_date": None,
                "is_eol": True,
                "subversions": ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"],
            },
            (
                "Version: 1\n"
                "Level: major\n"
                "Release-Date: 1994-01-26\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: yes\n"
                "Subversions: 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6\n"
            ),
        ),
        (
            "1",
            "supported",
            {
                "version": "1",
                "level": "major",
                "release_date": "1994-01-26",
                "is_released": True,
                "is_supported": False,
                "eol_date": None,
                "is_eol": True,
                "subversions": [],
            },
            (
                "Version: 1\n"
                "Level: major\n"
                "Release-Date: 1994-01-26\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: yes\n"
                "Subversions: \n"
            ),
        ),
        (
            "1",
            "not-eol",
            {
                "version": "1",
                "level": "major",
                "release_date": "1994-01-26",
                "is_released": True,
                "is_supported": False,
                "eol_date": None,
                "is_eol": True,
                "subversions": [],
            },
            (
                "Version: 1\n"
                "Level: major\n"
                "Release-Date: 1994-01-26\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: yes\n"
                "Subversions: \n"
            ),
        ),
        (
            "2",
            "released",
            {
                "version": "2",
                "level": "major",
                "release_date": "2000-10-16",
                "is_released": True,
                "is_supported": True,
                "eol_date": None,
                "is_eol": False,
                "subversions": ["2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"],
            },
            (
                "Version: 2\n"
                "Level: major\n"
                "Release-Date: 2000-10-16\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: no\n"
                "Subversions: 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7\n"
            ),
        ),
        (
            "2",
            "all",
            {
                "version": "2",
                "level": "major",
                "release_date": "2000-10-16",
                "is_released": True,
                "is_supported": True,
                "eol_date": None,
                "is_eol": False,
                "subversions": ["2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"],
            },
            (
                "Version: 2\n"
                "Level: major\n"
                "Release-Date: 2000-10-16\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: no\n"
                "Subversions: 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7\n"
            ),
        ),
        (
            "2",
            "supported",
            {
                "version": "2",
                "level": "major",
                "release_date": "2000-10-16",
                "is_released": True,
                "is_supported": True,
                "eol_date": None,
                "is_eol": False,
                "subversions": ["2.7"],
            },
            (
                "Version: 2\n"
                "Level: major\n"
                "Release-Date: 2000-10-16\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: no\n"
                "Subversions: 2.7\n"
            ),
        ),
        (
            "2",
            "not-eol",
            {
                "version": "2",
                "level": "major",
                "release_date": "2000-10-16",
                "is_released": True,
                "is_supported": True,
                "eol_date": None,
                "is_eol": False,
                "subversions": ["2.7"],
            },
            (
                "Version: 2\n"
                "Level: major\n"
                "Release-Date: 2000-10-16\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: no\n"
                "Subversions: 2.7\n"
            ),
        ),
        (
            "2.5",
            "released",
            {
                "version": "2.5",
                "level": "minor",
                "release_date": "2006-09-19",
                "is_released": True,
                "is_supported": False,
                "eol_date": None,
                "is_eol": True,
                "subversions": [
                    "2.5.0",
                    "2.5.1",
                    "2.5.2",
                    "2.5.3",
                    "2.5.4",
                    "2.5.5",
                    "2.5.6",
                ],
            },
            (
                "Version: 2.5\n"
                "Level: minor\n"
                "Release-Date: 2006-09-19\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: yes\n"
                "Subversions: 2.5.0, 2.5.1, 2.5.2, 2.5.3, 2.5.4, 2.5.5, 2.5.6\n"
            ),
        ),
        (
            "2.6",
            "released",
            {
                "version": "2.6",
                "level": "minor",
                "release_date": "2008-10-02",
                "is_released": True,
                "is_supported": False,
                "eol_date": "2013-10-29",
                "is_eol": True,
                "subversions": [
                    "2.6.0",
                    "2.6.1",
                    "2.6.2",
                    "2.6.3",
                    "2.6.4",
                    "2.6.5",
                    "2.6.6",
                    "2.6.7",
                    "2.6.8",
                    "2.6.9",
                ],
            },
            (
                "Version: 2.6\n"
                "Level: minor\n"
                "Release-Date: 2008-10-02\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: 2013-10-29\n"
                "Is-EOL: yes\n"
                "Subversions: 2.6.0, 2.6.1, 2.6.2, 2.6.3, 2.6.4, 2.6.5, 2.6.6,"
                " 2.6.7, 2.6.8, 2.6.9\n"
            ),
        ),
        (
            "2.6",
            "all",
            {
                "version": "2.6",
                "level": "minor",
                "release_date": "2008-10-02",
                "is_released": True,
                "is_supported": False,
                "eol_date": "2013-10-29",
                "is_eol": True,
                "subversions": [
                    "2.6.0",
                    "2.6.1",
                    "2.6.2",
                    "2.6.3",
                    "2.6.4",
                    "2.6.5",
                    "2.6.6",
                    "2.6.7",
                    "2.6.8",
                    "2.6.9",
                ],
            },
            (
                "Version: 2.6\n"
                "Level: minor\n"
                "Release-Date: 2008-10-02\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: 2013-10-29\n"
                "Is-EOL: yes\n"
                "Subversions: 2.6.0, 2.6.1, 2.6.2, 2.6.3, 2.6.4, 2.6.5, 2.6.6,"
                " 2.6.7, 2.6.8, 2.6.9\n"
            ),
        ),
        (
            "2.6",
            "supported",
            {
                "version": "2.6",
                "level": "minor",
                "release_date": "2008-10-02",
                "is_released": True,
                "is_supported": False,
                "eol_date": "2013-10-29",
                "is_eol": True,
                "subversions": [],
            },
            (
                "Version: 2.6\n"
                "Level: minor\n"
                "Release-Date: 2008-10-02\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: 2013-10-29\n"
                "Is-EOL: yes\n"
                "Subversions: \n"
            ),
        ),
        (
            "2.6",
            "not-eol",
            {
                "version": "2.6",
                "level": "minor",
                "release_date": "2008-10-02",
                "is_released": True,
                "is_supported": False,
                "eol_date": "2013-10-29",
                "is_eol": True,
                "subversions": [],
            },
            (
                "Version: 2.6\n"
                "Level: minor\n"
                "Release-Date: 2008-10-02\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: 2013-10-29\n"
                "Is-EOL: yes\n"
                "Subversions: \n"
            ),
        ),
        (
            "2.7",
            "released",
            {
                "version": "2.7",
                "level": "minor",
                "release_date": "2010-07-03",
                "is_released": True,
                "is_supported": True,
                "eol_date": "2020-01-01",
                "is_eol": False,
                "subversions": [
                    "2.7.0",
                    "2.7.1",
                    "2.7.2",
                    "2.7.3",
                    "2.7.4",
                    "2.7.5",
                    "2.7.6",
                    "2.7.7",
                    "2.7.8",
                    "2.7.9",
                    "2.7.10",
                    "2.7.11",
                    "2.7.12",
                    "2.7.13",
                    "2.7.14",
                    "2.7.15",
                    "2.7.16",
                ],
            },
            (
                "Version: 2.7\n"
                "Level: minor\n"
                "Release-Date: 2010-07-03\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: 2020-01-01\n"
                "Is-EOL: no\n"
                "Subversions: 2.7.0, 2.7.1, 2.7.2, 2.7.3, 2.7.4, 2.7.5, 2.7.6,"
                " 2.7.7, 2.7.8, 2.7.9, 2.7.10, 2.7.11, 2.7.12, 2.7.13, 2.7.14,"
                " 2.7.15, 2.7.16\n"
            ),
        ),
        (
            "3",
            "released",
            {
                "version": "3",
                "level": "major",
                "release_date": "2008-12-03",
                "is_released": True,
                "is_supported": True,
                "eol_date": None,
                "is_eol": False,
                "subversions": ["3.0", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7"],
            },
            (
                "Version: 3\n"
                "Level: major\n"
                "Release-Date: 2008-12-03\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: no\n"
                "Subversions: 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7\n"
            ),
        ),
        (
            "3",
            "all",
            {
                "version": "3",
                "level": "major",
                "release_date": "2008-12-03",
                "is_released": True,
                "is_supported": True,
                "eol_date": None,
                "is_eol": False,
                "subversions": [
                    "3.0",
                    "3.1",
                    "3.2",
                    "3.3",
                    "3.4",
                    "3.5",
                    "3.6",
                    "3.7",
                    "3.8",
                ],
            },
            (
                "Version: 3\n"
                "Level: major\n"
                "Release-Date: 2008-12-03\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: no\n"
                "Subversions: 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8\n"
            ),
        ),
        (
            "3",
            "not-eol",
            {
                "version": "3",
                "level": "major",
                "release_date": "2008-12-03",
                "is_released": True,
                "is_supported": True,
                "eol_date": None,
                "is_eol": False,
                "subversions": ["3.5", "3.6", "3.7", "3.8"],
            },
            (
                "Version: 3\n"
                "Level: major\n"
                "Release-Date: 2008-12-03\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: no\n"
                "Subversions: 3.5, 3.6, 3.7, 3.8\n"
            ),
        ),
        (
            "3",
            "supported",
            {
                "version": "3",
                "level": "major",
                "release_date": "2008-12-03",
                "is_released": True,
                "is_supported": True,
                "eol_date": None,
                "is_eol": False,
                "subversions": ["3.5", "3.6", "3.7"],
            },
            (
                "Version: 3\n"
                "Level: major\n"
                "Release-Date: 2008-12-03\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: no\n"
                "Subversions: 3.5, 3.6, 3.7\n"
            ),
        ),
        (
            "3.8",
            "released",
            {
                "version": "3.8",
                "level": "minor",
                "release_date": "2019-10-21",
                "is_released": False,
                "is_supported": False,
                "eol_date": "2024-10-01",
                "is_eol": False,
                "subversions": [],
            },
            (
                "Version: 3.8\n"
                "Level: minor\n"
                "Release-Date: 2019-10-21\n"
                "Is-Released: no\n"
                "Is-Supported: no\n"
                "EOL-Date: 2024-10-01\n"
                "Is-EOL: no\n"
                "Subversions: \n"
            ),
        ),
        (
            "3.8",
            "all",
            {
                "version": "3.8",
                "level": "minor",
                "release_date": "2019-10-21",
                "is_released": False,
                "is_supported": False,
                "eol_date": "2024-10-01",
                "is_eol": False,
                "subversions": ["3.8.0"],
            },
            (
                "Version: 3.8\n"
                "Level: minor\n"
                "Release-Date: 2019-10-21\n"
                "Is-Released: no\n"
                "Is-Supported: no\n"
                "EOL-Date: 2024-10-01\n"
                "Is-EOL: no\n"
                "Subversions: 3.8.0\n"
            ),
        ),
        (
            "3.8",
            "supported",
            {
                "version": "3.8",
                "level": "minor",
                "release_date": "2019-10-21",
                "is_released": False,
                "is_supported": False,
                "eol_date": "2024-10-01",
                "is_eol": False,
                "subversions": [],
            },
            (
                "Version: 3.8\n"
                "Level: minor\n"
                "Release-Date: 2019-10-21\n"
                "Is-Released: no\n"
                "Is-Supported: no\n"
                "EOL-Date: 2024-10-01\n"
                "Is-EOL: no\n"
                "Subversions: \n"
            ),
        ),
        (
            "3.8",
            "not-eol",
            {
                "version": "3.8",
                "level": "minor",
                "release_date": "2019-10-21",
                "is_released": False,
                "is_supported": False,
                "eol_date": "2024-10-01",
                "is_eol": False,
                "subversions": ["3.8.0"],
            },
            (
                "Version: 3.8\n"
                "Level: minor\n"
                "Release-Date: 2019-10-21\n"
                "Is-Released: no\n"
                "Is-Supported: no\n"
                "EOL-Date: 2024-10-01\n"
                "Is-EOL: no\n"
                "Subversions: 3.8.0\n"
            ),
        ),
    ],
)
def test_show(version: str, subversions: str, data: dict, headers: str) -> None:
    r = CliRunner().invoke(
        main, ["-d", DATA_FILE, "show", "--subversions", subversions, version]
    )
    assert r.exit_code == 0, show_result(r)
    assert r.output == headers
    if subversions == "released":
        r = CliRunner().invoke(main, ["-d", DATA_FILE, "show", version])
        assert r.exit_code == 0, show_result(r)
        assert r.output == headers
    r = CliRunner().invoke(
        main, ["-d", DATA_FILE, "show", "--json", "--subversions", subversions, version]
    )
    assert r.exit_code == 0, show_result(r)
    assert json.loads(r.output) == data


@pytest.mark.parametrize(
    "version,data,headers",
    [
        (
            "0.9.2",
            {
                "version": "0.9.2",
                "level": "micro",
                "release_date": None,
                "is_released": True,
                "is_supported": False,
                "eol_date": None,
                "is_eol": True,
            },
            (
                "Version: 0.9.2\n"
                "Level: micro\n"
                "Release-Date: UNKNOWN\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: UNKNOWN\n"
                "Is-EOL: yes\n"
            ),
        ),
        (
            "3.3.2",
            {
                "version": "3.3.2",
                "level": "micro",
                "release_date": "2013-05-15",
                "is_released": True,
                "is_supported": False,
                "eol_date": "2017-09-29",
                "is_eol": True,
            },
            (
                "Version: 3.3.2\n"
                "Level: micro\n"
                "Release-Date: 2013-05-15\n"
                "Is-Released: yes\n"
                "Is-Supported: no\n"
                "EOL-Date: 2017-09-29\n"
                "Is-EOL: yes\n"
            ),
        ),
        (
            "3.6.1",
            {
                "version": "3.6.1",
                "level": "micro",
                "release_date": "2017-03-21",
                "is_released": True,
                "is_supported": True,
                "eol_date": "2021-12-23",
                "is_eol": False,
            },
            (
                "Version: 3.6.1\n"
                "Level: micro\n"
                "Release-Date: 2017-03-21\n"
                "Is-Released: yes\n"
                "Is-Supported: yes\n"
                "EOL-Date: 2021-12-23\n"
                "Is-EOL: no\n"
            ),
        ),
        (
            "3.7.4",
            {
                "version": "3.7.4",
                "level": "micro",
                "release_date": "2019-06-24",
                "is_released": False,
                "is_supported": False,
                "eol_date": "2023-06-27",
                "is_eol": False,
            },
            (
                "Version: 3.7.4\n"
                "Level: micro\n"
                "Release-Date: 2019-06-24\n"
                "Is-Released: no\n"
                "Is-Supported: no\n"
                "EOL-Date: 2023-06-27\n"
                "Is-EOL: no\n"
            ),
        ),
    ],
)
@pytest.mark.parametrize("subversions", ["released", "all", "supported", "not-eol"])
def test_show_micro(version: str, subversions: str, data: dict, headers: str) -> None:
    r = CliRunner().invoke(
        main, ["-d", DATA_FILE, "show", "--subversions", subversions, version]
    )
    assert r.exit_code == 0, show_result(r)
    assert r.output == headers
    r = CliRunner().invoke(
        main, ["-d", DATA_FILE, "show", "--json", "--subversions", subversions, version]
    )
    assert r.exit_code == 0, show_result(r)
    assert json.loads(r.output) == data


def test_show_recent(mocker: MockerFixture) -> None:
    mocker.patch("time.time", return_value=1635992101)
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "show", "2"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == (
        "Version: 2\n"
        "Level: major\n"
        "Release-Date: 2000-10-16\n"
        "Is-Released: yes\n"
        "Is-Supported: no\n"
        "EOL-Date: 2020-01-01\n"
        "Is-EOL: yes\n"
        "Subversions: 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7\n"
    )
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "show", "--json", "2"])
    assert r.exit_code == 0, show_result(r)
    assert json.loads(r.output) == {
        "version": "2",
        "level": "major",
        "release_date": "2000-10-16",
        "is_released": True,
        "is_supported": False,
        "eol_date": "2020-01-01",
        "is_eol": True,
        "subversions": ["2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"],
    }


@pytest.mark.parametrize("v", ["", "1.2.3.4", "1.2.3rc1", "foobar", "a.b.c"])
def test_show_invalid_version(v: str) -> None:
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "show", v], standalone_mode=False)
    assert r.exit_code != 0
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "2.5.7", "3.9", "3.9.0", "5"])
def test_show_unknown_version(v: str) -> None:
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "show", v], standalone_mode=False)
    assert r.exit_code != 0
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == f"Unknown version: {v!r}"

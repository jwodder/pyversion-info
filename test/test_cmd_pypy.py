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
    mocker.patch("time.time", return_value=1635992101)
    # Time is now 2021-11-04T02:15:01+00:00.


def show_result(r: Result) -> str:
    if r.exception is not None:
        assert isinstance(r.exc_info, tuple)
        return "".join(format_exception(*r.exc_info))
    else:
        return r.output


@pytest.mark.parametrize(
    "mode,versions",
    [
        ("--all", ["1", "2", "4", "5", "6", "7", "8"]),
        ("--released", ["1", "2", "4", "5", "6", "7"]),
    ],
)
def test_cmd_list_major(mode: str, versions: List[str]) -> None:
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "--pypy", mode, "major"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == "".join(v + "\n" for v in versions)
    if mode == "--released":
        r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "--pypy", "major"])
        assert r.exit_code == 0, show_result(r)
        assert r.output == "".join(v + "\n" for v in versions)


RELEASED_MINOR = [
    "1.6",
    "1.7",
    "1.8",
    "1.9",
    "2.0",
    "2.1",
    "2.2",
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "4.0",
    "5.0",
    "5.1",
    "5.3",
    "5.4",
    "5.6",
    "5.7",
    "5.8",
    "5.9",
    "5.10",
    "6.0",
    "7.0",
    "7.1",
    "7.2",
    "7.3",
]


@pytest.mark.parametrize(
    "mode,versions",
    [
        ("--all", RELEASED_MINOR + ["7.4", "8.0"]),
        ("--released", RELEASED_MINOR),
    ],
)
def test_cmd_list_minor(mode: str, versions: List[str]) -> None:
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "--pypy", mode, "minor"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == "".join(v + "\n" for v in versions)
    if mode == "--released":
        r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "--pypy", "minor"])
        assert r.exit_code == 0, show_result(r)
        assert r.output == "".join(v + "\n" for v in versions)


RELEASED_MICRO = [
    "1.6.0",
    "1.7.0",
    "1.8.0",
    "1.9.0",
    "2.0.0",
    "2.0.1",
    "2.0.2",
    "2.1.0",
    "2.2.0",
    "2.2.1",
    "2.3.0",
    "2.3.1",
    "2.4.0",
    "2.5.0",
    "2.5.1",
    "2.6.0",
    "2.6.1",
    "4.0.0",
    "4.0.1",
    "5.0.0",
    "5.0.1",
    "5.1.0",
    "5.1.1",
    "5.1.2",
    "5.3.0",
    "5.3.1",
    "5.4.0",
    "5.4.1",
    "5.6.0",
    "5.7.0",
    "5.7.1",
    "5.8.0",
    "5.9.0",
    "5.10.0",
    "5.10.1",
    "6.0.0",
    "7.0.0",
    "7.1.0",
    "7.1.1",
    "7.2.0",
    "7.3.0",
    "7.3.1",
    "7.3.2",
    "7.3.3",
    "7.3.4",
    "7.3.5",
    "7.3.6",
    "7.3.7",
]


@pytest.mark.parametrize(
    "mode,versions",
    [
        ("--all", RELEASED_MICRO + ["7.4.0", "8.0.0"]),
        ("--released", RELEASED_MICRO),
    ],
)
def test_cmd_list_micro(mode: str, versions: List[str]) -> None:
    r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "--pypy", mode, "micro"])
    assert r.exit_code == 0, show_result(r)
    assert r.output == "".join(v + "\n" for v in versions)
    if mode == "--released":
        r = CliRunner().invoke(main, ["-d", DATA_FILE, "list", "--pypy", "micro"])
        assert r.exit_code == 0, show_result(r)
        assert r.output == "".join(v + "\n" for v in versions)


@pytest.mark.parametrize("level", ["major", "minor", "micro"])
def test_cmd_list_not_eol(level: str) -> None:
    r = CliRunner().invoke(
        main,
        ["-d", DATA_FILE, "list", "--pypy", "--not-eol", level],
        standalone_mode=False,
    )
    assert r.exit_code != 0
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == "'not-eol' only applies to CPython versions"


@pytest.mark.parametrize("level", ["major", "minor", "micro"])
def test_cmd_list_supported(level: str) -> None:
    r = CliRunner().invoke(
        main,
        ["-d", DATA_FILE, "list", "--pypy", "--supported", level],
        standalone_mode=False,
    )
    assert r.exit_code != 0
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == "'supported' only applies to CPython versions"


@pytest.mark.parametrize(
    "version,data,headers",
    [
        (
            "1",
            {
                "version": "1",
                "level": "major",
                "release_date": "2011-08-18",
                "is_released": True,
                "subversions": ["1.6", "1.7", "1.8", "1.9"],
                "cpython_series": ["2.7"],
            },
            (
                "Version: 1\n"
                "Level: major\n"
                "Release-Date: 2011-08-18\n"
                "Is-Released: yes\n"
                "Subversions: 1.6, 1.7, 1.8, 1.9\n"
                "CPython-Series: 2.7\n"
            ),
        ),
        (
            "2",
            {
                "version": "2",
                "level": "major",
                "release_date": "2013-05-09",
                "is_released": True,
                "subversions": ["2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6"],
                "cpython_series": ["2.7", "3.2"],
            },
            (
                "Version: 2\n"
                "Level: major\n"
                "Release-Date: 2013-05-09\n"
                "Is-Released: yes\n"
                "Subversions: 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6\n"
                "CPython-Series: 2.7, 3.2\n"
            ),
        ),
        (
            "2.5",
            {
                "version": "2.5",
                "level": "minor",
                "release_date": "2015-02-03",
                "is_released": True,
                "subversions": ["2.5.0", "2.5.1"],
                "cpython_series": ["2.7"],
            },
            (
                "Version: 2.5\n"
                "Level: minor\n"
                "Release-Date: 2015-02-03\n"
                "Is-Released: yes\n"
                "Subversions: 2.5.0, 2.5.1\n"
                "CPython-Series: 2.7\n"
            ),
        ),
        (
            "7.3.7",
            {
                "version": "7.3.7",
                "level": "micro",
                "release_date": "2021-10-25",
                "is_released": True,
                "cpython": ["3.7.12", "3.8.12"],
            },
            (
                "Version: 7.3.7\n"
                "Level: micro\n"
                "Release-Date: 2021-10-25\n"
                "Is-Released: yes\n"
                "CPython: 3.7.12, 3.8.12\n"
            ),
        ),
        (
            "8.0.0",
            {
                "version": "8.0.0",
                "level": "micro",
                "release_date": None,
                "is_released": False,
                "cpython": ["3.11.1"],
            },
            (
                "Version: 8.0.0\n"
                "Level: micro\n"
                "Release-Date: UNKNOWN\n"
                "Is-Released: no\n"
                "CPython: 3.11.1\n"
            ),
        ),
    ],
)
@pytest.mark.parametrize("subversions", ["released", "all"])
def test_show(version: str, subversions: str, data: dict, headers: str) -> None:
    r = CliRunner().invoke(
        main, ["-d", DATA_FILE, "show", "--pypy", "--subversions", subversions, version]
    )
    assert r.exit_code == 0, show_result(r)
    assert r.output == headers
    r = CliRunner().invoke(
        main,
        [
            "-d",
            DATA_FILE,
            "show",
            "--pypy",
            "--json",
            "--subversions",
            subversions,
            version,
        ],
    )
    assert r.exit_code == 0, show_result(r)
    assert json.loads(r.output) == data


@pytest.mark.parametrize(
    "version,subversions,data,headers",
    [
        (
            "7",
            "all",
            {
                "version": "7",
                "level": "major",
                "release_date": "2019-02-06",
                "is_released": True,
                "subversions": ["7.0", "7.1", "7.2", "7.3", "7.4"],
                "cpython_series": ["2.7", "3.5", "3.6", "3.7", "3.8", "3.9"],
            },
            (
                "Version: 7\n"
                "Level: major\n"
                "Release-Date: 2019-02-06\n"
                "Is-Released: yes\n"
                "Subversions: 7.0, 7.1, 7.2, 7.3, 7.4\n"
                "CPython-Series: 2.7, 3.5, 3.6, 3.7, 3.8, 3.9\n"
            ),
        ),
        (
            "7",
            "released",
            {
                "version": "7",
                "level": "major",
                "release_date": "2019-02-06",
                "is_released": True,
                "subversions": ["7.0", "7.1", "7.2", "7.3"],
                "cpython_series": ["2.7", "3.5", "3.6", "3.7", "3.8"],
            },
            (
                "Version: 7\n"
                "Level: major\n"
                "Release-Date: 2019-02-06\n"
                "Is-Released: yes\n"
                "Subversions: 7.0, 7.1, 7.2, 7.3\n"
                "CPython-Series: 2.7, 3.5, 3.6, 3.7, 3.8\n"
            ),
        ),
        (
            "8.0",
            "all",
            {
                "version": "8.0",
                "level": "minor",
                "release_date": None,
                "is_released": False,
                "subversions": ["8.0.0"],
                "cpython_series": ["3.11"],
            },
            (
                "Version: 8.0\n"
                "Level: minor\n"
                "Release-Date: UNKNOWN\n"
                "Is-Released: no\n"
                "Subversions: 8.0.0\n"
                "CPython-Series: 3.11\n"
            ),
        ),
        (
            "8.0",
            "released",
            {
                "version": "8.0",
                "level": "minor",
                "release_date": None,
                "is_released": False,
                "subversions": [],
                "cpython_series": [],
            },
            (
                "Version: 8.0\n"
                "Level: minor\n"
                "Release-Date: UNKNOWN\n"
                "Is-Released: no\n"
                "Subversions: \n"
                "CPython-Series: \n"
            ),
        ),
    ],
)
def test_show_not_all_released(
    version: str, subversions: str, data: dict, headers: str
) -> None:
    r = CliRunner().invoke(
        main, ["-d", DATA_FILE, "show", "--pypy", "--subversions", subversions, version]
    )
    assert r.exit_code == 0, show_result(r)
    assert r.output == headers
    if subversions == "released":
        r = CliRunner().invoke(main, ["-d", DATA_FILE, "show", "--pypy", version])
        assert r.exit_code == 0, show_result(r)
        assert r.output == headers
    r = CliRunner().invoke(
        main,
        [
            "-d",
            DATA_FILE,
            "show",
            "--pypy",
            "--json",
            "--subversions",
            subversions,
            version,
        ],
    )
    assert r.exit_code == 0, show_result(r)
    assert json.loads(r.output) == data


@pytest.mark.parametrize("v", ["7", "7.3"])
def test_cmd_show_not_eol(v: str) -> None:
    r = CliRunner().invoke(
        main,
        ["-d", DATA_FILE, "show", "--pypy", "--subversions", "not-eol", v],
        standalone_mode=False,
    )
    assert r.exit_code != 0
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == "'not-eol' only applies to CPython versions"


@pytest.mark.parametrize("v", ["7", "7.3"])
def test_cmd_show_supported(v: str) -> None:
    r = CliRunner().invoke(
        main,
        ["-d", DATA_FILE, "show", "--pypy", "--subversions", "supported", v],
        standalone_mode=False,
    )
    assert r.exit_code != 0
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == "'supported' only applies to CPython versions"


@pytest.mark.parametrize("v", ["", "1.2.3.4", "1.2.3rc1", "foobar", "a.b.c"])
def test_show_invalid_version(v: str) -> None:
    r = CliRunner().invoke(
        main, ["-d", DATA_FILE, "show", "--pypy", v], standalone_mode=False
    )
    assert r.exit_code != 0
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "1.5", "3", "7.3.9", "9.0.0"])
def test_show_unknown_version(v: str) -> None:
    r = CliRunner().invoke(
        main, ["-d", DATA_FILE, "show", "--pypy", v], standalone_mode=False
    )
    assert r.exit_code != 0
    assert isinstance(r.exception, click.UsageError)
    assert str(r.exception) == f"Unknown version: {v!r}"

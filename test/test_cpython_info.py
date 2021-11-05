from datetime import date
from typing import List, Optional
import pytest
from pytest_mock import MockerFixture
from pyversion_info import CPythonVersionInfo, UnknownVersionError, VersionDatabase

INVALID_VERSIONS = ["", "1.2.3.4", "1.2.3rc1", "foobar", "a.b.c"]


@pytest.fixture(autouse=True)
def use_fixed_date(mocker: MockerFixture) -> None:
    # Mocking/monkeypatching just the `today()` method of `date` doesn't seem
    # to be an option, and monkeypatching the `date` class with a custom class
    # that just implements `today()` causes problems on PyPy.  Fortunately,
    # both CPython and PyPy implement `date.today()` by calling `time.time()`,
    # so we just need to mock that and hope the implementation never changes.
    mocker.patch("time.time", return_value=1556052408)
    # Time is now 2019-04-23T16:46:48-04:00.


@pytest.fixture(scope="module")
def pyvinfo(version_database: VersionDatabase) -> CPythonVersionInfo:
    return version_database.cpython


def test_supported_series(pyvinfo: CPythonVersionInfo) -> None:
    assert pyvinfo.supported_series() == ["2.7", "3.5", "3.6", "3.7"]


def test_major_versions(pyvinfo: CPythonVersionInfo) -> None:
    assert pyvinfo.major_versions() == ["0", "1", "2", "3", "4"]


def test_minor_versions(pyvinfo: CPythonVersionInfo) -> None:
    assert pyvinfo.minor_versions() == [
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
    ]


def test_micro_versions(pyvinfo: CPythonVersionInfo) -> None:
    assert pyvinfo.micro_versions() == [
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
    ]


@pytest.mark.parametrize(
    "v,rel",
    [
        ("0", date(1991, 2, 20)),
        ("0.9", date(1991, 2, 20)),
        ("0.9.0", date(1991, 2, 20)),
        ("0.9.1", date(1991, 2, 21)),
        ("0.9.2", None),
        ("0.9.4", date(1991, 12, 24)),
        ("0.9.5", date(1992, 1, 2)),
        ("0.9.6", date(1992, 4, 6)),
        ("0.9.8", date(1993, 1, 9)),
        ("0.9.9", date(1993, 7, 29)),
        ("1", date(1994, 1, 26)),
        ("1.0", date(1994, 1, 26)),
        ("1.0.0", date(1994, 1, 26)),
        ("1.0.1", date(1994, 2, 15)),
        ("1.0.2", date(1994, 2, 15)),
        ("1.0.3", date(1994, 5, 4)),
        ("1.0.4", date(1994, 7, 14)),
        ("1.1", date(1994, 10, 11)),
        ("1.1.0", date(1994, 10, 11)),
        ("1.1.1", date(1994, 11, 10)),
        ("1.2", date(1995, 4, 13)),
        ("1.2.0", date(1995, 4, 13)),
        ("1.3", date(1995, 10, 13)),
        ("1.3.0", date(1995, 10, 13)),
        ("1.4", date(1996, 10, 25)),
        ("1.4.0", date(1996, 10, 25)),
        ("1.5", date(1997, 12, 31)),
        ("1.5.0", date(1997, 12, 31)),
        ("1.5.1", date(1998, 4, 14)),
        ("1.5.2", date(1999, 4, 13)),
        ("1.6", date(2000, 9, 5)),
        ("1.6.0", date(2000, 9, 5)),
        ("1.6.1", date(2000, 9, 30)),
        ("2", date(2000, 10, 16)),
        ("2.0", date(2000, 10, 16)),
        ("2.0.0", date(2000, 10, 16)),
        ("2.0.1", date(2001, 6, 22)),
        ("2.1", date(2001, 4, 17)),
        ("2.1.0", date(2001, 4, 17)),
        ("2.1.1", date(2001, 7, 20)),
        ("2.1.2", date(2002, 1, 16)),
        ("2.1.3", date(2002, 4, 9)),
        ("2.2", date(2001, 12, 21)),
        ("2.2.0", date(2001, 12, 21)),
        ("2.2.1", date(2002, 4, 10)),
        ("2.2.2", date(2002, 10, 14)),
        ("2.2.3", date(2003, 5, 30)),
        ("2.3", date(2003, 7, 29)),
        ("2.3.0", date(2003, 7, 29)),
        ("2.3.1", date(2003, 9, 23)),
        ("2.3.2", date(2003, 10, 3)),
        ("2.3.3", date(2003, 12, 19)),
        ("2.3.4", date(2004, 5, 27)),
        ("2.3.5", date(2005, 2, 8)),
        ("2.3.6", date(2006, 11, 1)),
        ("2.3.7", date(2008, 3, 11)),
        ("2.4", date(2004, 11, 30)),
        ("2.4.0", date(2004, 11, 30)),
        ("2.4.1", date(2005, 3, 30)),
        ("2.4.2", date(2005, 9, 27)),
        ("2.4.3", date(2006, 4, 15)),
        ("2.4.4", date(2006, 10, 18)),
        ("2.4.5", date(2008, 3, 11)),
        ("2.4.6", date(2008, 12, 19)),
        ("2.5", date(2006, 9, 19)),
        ("2.5.0", date(2006, 9, 19)),
        ("2.5.1", date(2007, 4, 19)),
        ("2.5.2", date(2008, 2, 21)),
        ("2.5.3", date(2008, 12, 19)),
        ("2.5.4", date(2008, 12, 23)),
        ("2.5.5", date(2010, 1, 31)),
        ("2.5.6", date(2011, 5, 26)),
        ("2.6", date(2008, 10, 2)),
        ("2.6.0", date(2008, 10, 2)),
        ("2.6.1", date(2008, 12, 4)),
        ("2.6.2", date(2009, 4, 14)),
        ("2.6.3", date(2009, 10, 2)),
        ("2.6.4", date(2009, 10, 26)),
        ("2.6.5", date(2010, 3, 18)),
        ("2.6.6", date(2010, 8, 24)),
        ("2.6.7", date(2011, 6, 3)),
        ("2.6.8", date(2012, 4, 10)),
        ("2.6.9", date(2013, 10, 29)),
        ("2.7", date(2010, 7, 3)),
        ("2.7.0", date(2010, 7, 3)),
        ("2.7.1", date(2010, 11, 27)),
        ("2.7.2", date(2011, 6, 11)),
        ("2.7.3", date(2012, 4, 9)),
        ("2.7.4", date(2013, 4, 6)),
        ("2.7.5", date(2013, 5, 12)),
        ("2.7.6", date(2013, 11, 10)),
        ("2.7.7", date(2014, 6, 1)),
        ("2.7.8", date(2014, 7, 2)),
        ("2.7.9", date(2014, 12, 10)),
        ("2.7.10", date(2015, 5, 23)),
        ("2.7.11", date(2015, 12, 5)),
        ("2.7.12", date(2016, 6, 25)),
        ("2.7.13", date(2016, 12, 17)),
        ("2.7.14", date(2017, 9, 16)),
        ("2.7.15", date(2018, 5, 1)),
        ("2.7.16", date(2019, 3, 4)),
        ("2.7.17", date(2019, 6, 15)),
        ("2.7.18", date(2020, 1, 1)),
        ("3", date(2008, 12, 3)),
        ("3.0", date(2008, 12, 3)),
        ("3.0.0", date(2008, 12, 3)),
        ("3.0.1", date(2009, 2, 13)),
        ("3.1", date(2009, 6, 26)),
        ("3.1.0", date(2009, 6, 26)),
        ("3.1.1", date(2009, 8, 17)),
        ("3.1.2", date(2010, 3, 20)),
        ("3.1.3", date(2010, 11, 27)),
        ("3.1.4", date(2011, 6, 11)),
        ("3.1.5", date(2012, 4, 9)),
        ("3.2", date(2011, 2, 20)),
        ("3.2.0", date(2011, 2, 20)),
        ("3.2.1", date(2011, 7, 9)),
        ("3.2.2", date(2011, 9, 3)),
        ("3.2.3", date(2012, 4, 10)),
        ("3.2.4", date(2013, 4, 6)),
        ("3.2.5", date(2013, 5, 15)),
        ("3.2.6", date(2014, 10, 12)),
        ("3.3", date(2012, 9, 29)),
        ("3.3.0", date(2012, 9, 29)),
        ("3.3.1", date(2013, 4, 6)),
        ("3.3.2", date(2013, 5, 15)),
        ("3.3.3", date(2013, 11, 17)),
        ("3.3.4", date(2014, 2, 9)),
        ("3.3.5", date(2014, 3, 9)),
        ("3.3.6", date(2014, 10, 12)),
        ("3.3.7", date(2017, 9, 19)),
        ("3.4", date(2014, 3, 17)),
        ("3.4.0", date(2014, 3, 17)),
        ("3.4.1", date(2014, 5, 19)),
        ("3.4.2", date(2014, 10, 13)),
        ("3.4.3", date(2015, 2, 25)),
        ("3.4.4", date(2015, 12, 21)),
        ("3.4.5", date(2016, 6, 27)),
        ("3.4.6", date(2017, 1, 17)),
        ("3.4.7", date(2017, 8, 9)),
        ("3.4.8", date(2018, 2, 5)),
        ("3.4.9", date(2018, 8, 2)),
        ("3.4.10", date(2019, 3, 18)),
        ("3.5", date(2015, 9, 13)),
        ("3.5.0", date(2015, 9, 13)),
        ("3.5.1", date(2015, 12, 7)),
        ("3.5.2", date(2016, 6, 27)),
        ("3.5.3", date(2017, 1, 17)),
        ("3.5.4", date(2017, 8, 8)),
        ("3.5.5", date(2018, 2, 5)),
        ("3.5.6", date(2018, 8, 2)),
        ("3.5.7", date(2019, 3, 18)),
        ("3.6", date(2016, 12, 23)),
        ("3.6.0", date(2016, 12, 23)),
        ("3.6.1", date(2017, 3, 21)),
        ("3.6.2", date(2017, 7, 17)),
        ("3.6.3", date(2017, 10, 3)),
        ("3.6.4", date(2017, 12, 19)),
        ("3.6.5", date(2018, 3, 28)),
        ("3.6.6", date(2018, 6, 27)),
        ("3.6.7", date(2018, 10, 20)),
        ("3.6.8", date(2018, 12, 24)),
        ("3.7", date(2018, 6, 27)),
        ("3.7.0", date(2018, 6, 27)),
        ("3.7.1", date(2018, 10, 20)),
        ("3.7.2", date(2018, 12, 24)),
        ("3.7.3", date(2019, 3, 25)),
        ("3.7.4", date(2019, 6, 24)),
        ("3.8", date(2019, 10, 21)),
        ("3.8.0", date(2019, 10, 21)),
        ("4", None),
        ("4.0", None),
        ("4.0.0", None),
    ],
)
def test_release_date(pyvinfo: CPythonVersionInfo, v: str, rel: Optional[date]) -> None:
    assert pyvinfo.release_date(v) == rel


@pytest.mark.parametrize("v", INVALID_VERSIONS)
def test_release_date_invalid(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pyvinfo.release_date(v)
    assert str(excinfo.value) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "2.5.7", "3.9", "3.9.0", "5"])
def test_release_date_unknown(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(UnknownVersionError) as excinfo:
        pyvinfo.release_date(v)
    assert str(excinfo.value) == f"Unknown version: {v!r}"
    assert excinfo.value.version == v


@pytest.mark.parametrize(
    "v,rel",
    [
        ("0", True),
        ("0.9", True),
        ("0.9.0", True),
        ("0.9.1", True),
        ("0.9.2", True),
        ("0.9.4", True),
        ("0.9.5", True),
        ("0.9.6", True),
        ("0.9.8", True),
        ("0.9.9", True),
        ("1", True),
        ("1.0", True),
        ("1.0.0", True),
        ("1.0.1", True),
        ("1.0.2", True),
        ("1.0.3", True),
        ("1.0.4", True),
        ("1.1", True),
        ("1.1.0", True),
        ("1.1.1", True),
        ("1.2", True),
        ("1.2.0", True),
        ("1.3", True),
        ("1.3.0", True),
        ("1.4", True),
        ("1.4.0", True),
        ("1.5", True),
        ("1.5.0", True),
        ("1.5.1", True),
        ("1.5.2", True),
        ("1.6", True),
        ("1.6.0", True),
        ("1.6.1", True),
        ("2", True),
        ("2.0", True),
        ("2.0.0", True),
        ("2.0.1", True),
        ("2.1", True),
        ("2.1.0", True),
        ("2.1.1", True),
        ("2.1.2", True),
        ("2.1.3", True),
        ("2.2", True),
        ("2.2.0", True),
        ("2.2.1", True),
        ("2.2.2", True),
        ("2.2.3", True),
        ("2.3", True),
        ("2.3.0", True),
        ("2.3.1", True),
        ("2.3.2", True),
        ("2.3.3", True),
        ("2.3.4", True),
        ("2.3.5", True),
        ("2.3.6", True),
        ("2.3.7", True),
        ("2.4", True),
        ("2.4.0", True),
        ("2.4.1", True),
        ("2.4.2", True),
        ("2.4.3", True),
        ("2.4.4", True),
        ("2.4.5", True),
        ("2.4.6", True),
        ("2.5", True),
        ("2.5.0", True),
        ("2.5.1", True),
        ("2.5.2", True),
        ("2.5.3", True),
        ("2.5.4", True),
        ("2.5.5", True),
        ("2.5.6", True),
        ("2.6", True),
        ("2.6.0", True),
        ("2.6.1", True),
        ("2.6.2", True),
        ("2.6.3", True),
        ("2.6.4", True),
        ("2.6.5", True),
        ("2.6.6", True),
        ("2.6.7", True),
        ("2.6.8", True),
        ("2.6.9", True),
        ("2.7", True),
        ("2.7.0", True),
        ("2.7.1", True),
        ("2.7.2", True),
        ("2.7.3", True),
        ("2.7.4", True),
        ("2.7.5", True),
        ("2.7.6", True),
        ("2.7.7", True),
        ("2.7.8", True),
        ("2.7.9", True),
        ("2.7.10", True),
        ("2.7.11", True),
        ("2.7.12", True),
        ("2.7.13", True),
        ("2.7.14", True),
        ("2.7.15", True),
        ("2.7.16", True),
        ("2.7.17", False),
        ("2.7.18", False),
        ("3", True),
        ("3.0", True),
        ("3.0.0", True),
        ("3.0.1", True),
        ("3.1", True),
        ("3.1.0", True),
        ("3.1.1", True),
        ("3.1.2", True),
        ("3.1.3", True),
        ("3.1.4", True),
        ("3.1.5", True),
        ("3.2", True),
        ("3.2.0", True),
        ("3.2.1", True),
        ("3.2.2", True),
        ("3.2.3", True),
        ("3.2.4", True),
        ("3.2.5", True),
        ("3.2.6", True),
        ("3.3", True),
        ("3.3.0", True),
        ("3.3.1", True),
        ("3.3.2", True),
        ("3.3.3", True),
        ("3.3.4", True),
        ("3.3.5", True),
        ("3.3.6", True),
        ("3.3.7", True),
        ("3.4", True),
        ("3.4.0", True),
        ("3.4.1", True),
        ("3.4.2", True),
        ("3.4.3", True),
        ("3.4.4", True),
        ("3.4.5", True),
        ("3.4.6", True),
        ("3.4.7", True),
        ("3.4.8", True),
        ("3.4.9", True),
        ("3.4.10", True),
        ("3.5", True),
        ("3.5.0", True),
        ("3.5.1", True),
        ("3.5.2", True),
        ("3.5.3", True),
        ("3.5.4", True),
        ("3.5.5", True),
        ("3.5.6", True),
        ("3.5.7", True),
        ("3.6", True),
        ("3.6.0", True),
        ("3.6.1", True),
        ("3.6.2", True),
        ("3.6.3", True),
        ("3.6.4", True),
        ("3.6.5", True),
        ("3.6.6", True),
        ("3.6.7", True),
        ("3.6.8", True),
        ("3.7", True),
        ("3.7.0", True),
        ("3.7.1", True),
        ("3.7.2", True),
        ("3.7.3", True),
        ("3.7.4", False),
        ("3.8", False),
        ("3.8.0", False),
        ("4", False),
        ("4.0", False),
        ("4.0.0", False),
    ],
)
def test_is_released(pyvinfo: CPythonVersionInfo, v: str, rel: bool) -> None:
    assert pyvinfo.is_released(v) is rel


@pytest.mark.parametrize("v", INVALID_VERSIONS)
def test_is_released_invalid(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pyvinfo.is_released(v)
    assert str(excinfo.value) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "2.5.7", "3.9", "3.9.0", "5"])
def test_is_released_unknown(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(UnknownVersionError) as excinfo:
        pyvinfo.is_released(v)
    assert str(excinfo.value) == f"Unknown version: {v!r}"
    assert excinfo.value.version == v


@pytest.mark.parametrize(
    "version,eol",
    [
        ("0", None),
        ("0.9", None),
        ("1", None),
        ("1.0", None),
        ("1.1", None),
        ("1.2", None),
        ("1.3", None),
        ("1.4", None),
        ("1.5", None),
        ("1.6", None),
        ("2", None),
        ("2.0", None),
        ("2.1", None),
        ("2.2", None),
        ("2.3", None),
        ("2.4", None),
        ("2.5", None),
        ("2.6", date(2013, 10, 29)),
        ("2.6.9", date(2013, 10, 29)),
        ("2.7", date(2020, 1, 1)),
        ("2.7.0", date(2020, 1, 1)),
        ("3", None),
        ("3.0", date(2009, 1, 13)),
        ("3.1", date(2012, 6, 1)),
        ("3.2", date(2016, 2, 20)),
        ("3.3", date(2017, 9, 29)),
        ("3.4", date(2019, 3, 19)),
        ("3.5", date(2020, 9, 13)),
        ("3.6", date(2021, 12, 23)),
        ("3.7", date(2023, 6, 27)),
        ("3.8", date(2024, 10, 1)),
        ("4", None),
        ("4.0", None),
    ],
)
def test_eol_date(
    pyvinfo: CPythonVersionInfo, version: str, eol: Optional[date]
) -> None:
    assert pyvinfo.eol_date(version) == eol


def test_eol_date_recent(mocker: MockerFixture, pyvinfo: CPythonVersionInfo) -> None:
    mocker.patch("time.time", return_value=1635992101)
    assert pyvinfo.eol_date("2") == date(2020, 1, 1)


@pytest.mark.parametrize("v", INVALID_VERSIONS)
def test_eol_date_invalid(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pyvinfo.eol_date(v)
    assert str(excinfo.value) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "3.9"])
def test_eol_date_unknown(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(UnknownVersionError) as excinfo:
        pyvinfo.eol_date(v)
    assert str(excinfo.value) == f"Unknown version: {v!r}"
    assert excinfo.value.version == v


@pytest.mark.parametrize(
    "version,is_eol",
    [
        ("0", True),
        ("0.9", True),
        ("1", True),
        ("1.0", True),
        ("1.1", True),
        ("1.2", True),
        ("1.3", True),
        ("1.4", True),
        ("1.5", True),
        ("1.6", True),
        ("2", False),
        ("2.0", True),
        ("2.1", True),
        ("2.2", True),
        ("2.3", True),
        ("2.4", True),
        ("2.5", True),
        ("2.6", True),
        ("2.6.9", True),
        ("2.7", False),
        ("2.7.0", False),
        ("3", False),
        ("3.0", True),
        ("3.1", True),
        ("3.2", True),
        ("3.3", True),
        ("3.4", True),
        ("3.5", False),
        ("3.6", False),
        ("3.7", False),
        ("3.8", False),
        ("4", False),
        ("4.0", False),
    ],
)
def test_is_eol(pyvinfo: CPythonVersionInfo, version: str, is_eol: bool) -> None:
    assert pyvinfo.is_eol(version) is is_eol


def test_is_eol_recent(mocker: MockerFixture, pyvinfo: CPythonVersionInfo) -> None:
    mocker.patch("time.time", return_value=1635992101)
    assert pyvinfo.is_eol("2") is True


@pytest.mark.parametrize("v", INVALID_VERSIONS)
def test_is_eol_invalid(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pyvinfo.is_eol(v)
    assert str(excinfo.value) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "3.9"])
def test_is_eol_unknown(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(UnknownVersionError) as excinfo:
        pyvinfo.is_eol(v)
    assert str(excinfo.value) == f"Unknown version: {v!r}"
    assert excinfo.value.version == v


@pytest.mark.parametrize(
    "series,is_supported",
    [
        ("0", False),
        ("0.9", False),
        ("1", False),
        ("1.0", False),
        ("1.1", False),
        ("1.2", False),
        ("1.3", False),
        ("1.4", False),
        ("1.5", False),
        ("1.6", False),
        ("2", True),
        ("2.0", False),
        ("2.1", False),
        ("2.2", False),
        ("2.3", False),
        ("2.4", False),
        ("2.5", False),
        ("2.5.7", False),
        ("2.6", False),
        ("2.7", True),
        ("2.7.1", True),
        ("3", True),
        ("3.0", False),
        ("3.0.0", False),
        ("3.1", False),
        ("3.1.0", False),
        ("3.2", False),
        ("3.3", False),
        ("3.4", False),
        ("3.5", True),
        ("3.6", True),
        ("3.7", True),
        ("3.8", False),
    ],
)
def test_is_supported(
    pyvinfo: CPythonVersionInfo, series: str, is_supported: bool
) -> None:
    assert pyvinfo.is_supported(series) is is_supported


@pytest.mark.parametrize("v", INVALID_VERSIONS)
def test_is_supported_invalid(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pyvinfo.is_supported(v)
    assert str(excinfo.value) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "3.9"])
def test_is_supported_unknown(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(UnknownVersionError) as excinfo:
        pyvinfo.is_supported(v)
    assert str(excinfo.value) == f"Unknown version: {v!r}"
    assert excinfo.value.version == v


@pytest.mark.parametrize(
    "v,subs",
    [
        ("0", ["0.9"]),
        (
            "0.9",
            ["0.9.0", "0.9.1", "0.9.2", "0.9.4", "0.9.5", "0.9.6", "0.9.8", "0.9.9"],
        ),
        ("1", ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"]),
        ("1.0", ["1.0.0", "1.0.1", "1.0.2", "1.0.3", "1.0.4"]),
        ("1.1", ["1.1.0", "1.1.1"]),
        ("1.2", ["1.2.0"]),
        ("1.3", ["1.3.0"]),
        ("1.4", ["1.4.0"]),
        ("1.5", ["1.5.0", "1.5.1", "1.5.2"]),
        ("1.6", ["1.6.0", "1.6.1"]),
        ("2", ["2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"]),
        ("2.0", ["2.0.0", "2.0.1"]),
        ("2.1", ["2.1.0", "2.1.1", "2.1.2", "2.1.3"]),
        ("2.2", ["2.2.0", "2.2.1", "2.2.2", "2.2.3"]),
        (
            "2.3",
            ["2.3.0", "2.3.1", "2.3.2", "2.3.3", "2.3.4", "2.3.5", "2.3.6", "2.3.7"],
        ),
        ("2.4", ["2.4.0", "2.4.1", "2.4.2", "2.4.3", "2.4.4", "2.4.5", "2.4.6"]),
        ("2.5", ["2.5.0", "2.5.1", "2.5.2", "2.5.3", "2.5.4", "2.5.5", "2.5.6"]),
        (
            "2.6",
            [
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
        ),
        (
            "2.7",
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
            ],
        ),
        ("3", ["3.0", "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8"]),
        ("3.0", ["3.0.0", "3.0.1"]),
        ("3.1", ["3.1.0", "3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.1.5"]),
        ("3.2", ["3.2.0", "3.2.1", "3.2.2", "3.2.3", "3.2.4", "3.2.5", "3.2.6"]),
        (
            "3.3",
            ["3.3.0", "3.3.1", "3.3.2", "3.3.3", "3.3.4", "3.3.5", "3.3.6", "3.3.7"],
        ),
        (
            "3.4",
            [
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
            ],
        ),
        (
            "3.5",
            ["3.5.0", "3.5.1", "3.5.2", "3.5.3", "3.5.4", "3.5.5", "3.5.6", "3.5.7"],
        ),
        (
            "3.6",
            [
                "3.6.0",
                "3.6.1",
                "3.6.2",
                "3.6.3",
                "3.6.4",
                "3.6.5",
                "3.6.6",
                "3.6.7",
                "3.6.8",
            ],
        ),
        ("3.7", ["3.7.0", "3.7.1", "3.7.2", "3.7.3", "3.7.4"]),
        ("3.8", ["3.8.0"]),
    ],
)
def test_subversions(pyvinfo: CPythonVersionInfo, v: str, subs: List[str]) -> None:
    assert pyvinfo.subversions(v) == subs


@pytest.mark.parametrize("v", INVALID_VERSIONS)
def test_subversions_invalid(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pyvinfo.subversions(v)
    assert str(excinfo.value) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["2.5.7", "3.7.3", "3.9.0"])
def test_subversions_invalid_micro(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pyvinfo.subversions(v)
    assert str(excinfo.value) == f"Micro versions do not have subversions: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "3.9", "5"])
def test_subversions_unknown(pyvinfo: CPythonVersionInfo, v: str) -> None:
    with pytest.raises(UnknownVersionError) as excinfo:
        pyvinfo.subversions(v)
    assert str(excinfo.value) == f"Unknown version: {v!r}"
    assert excinfo.value.version == v

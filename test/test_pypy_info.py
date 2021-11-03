from typing import List
import pytest
from pyversion_info import PyPyVersionInfo, UnknownVersionError, VersionDatabase

INVALID_VERSIONS = ["", "1.2.3.4", "1.2.3rc1", "foobar", "a.b.c"]


@pytest.fixture(scope="module")
def pypyinfo(version_database: VersionDatabase) -> PyPyVersionInfo:
    return version_database.pypy


@pytest.mark.parametrize(
    "version,cpythons",
    [
        ("1.6.0", ["2.7.1"]),
        ("1.7.0", ["2.7.1"]),
        ("1.8.0", ["2.7.2"]),
        ("1.9.0", ["2.7.2"]),
        ("2.0.0", ["2.7.3"]),
        ("2.0.1", ["2.7.3"]),
        ("2.0.2", ["2.7.3"]),
        ("2.1.0", ["2.7.3"]),
        ("2.2.0", ["2.7.3"]),
        ("2.2.1", ["2.7.3"]),
        ("2.3.0", ["2.7.6"]),
        ("2.3.1", ["2.7.6", "3.2.5"]),
        ("2.4.0", ["2.7.8", "3.2.5"]),
        ("2.5.0", ["2.7.8"]),
        ("2.5.1", ["2.7.9"]),
        ("2.6.0", ["2.7.9"]),
        ("2.6.1", ["2.7.10"]),
        ("4.0.0", ["2.7.10"]),
        ("4.0.1", ["2.7.10"]),
        ("5.0.0", ["2.7.10"]),
        ("5.0.1", ["2.7.10"]),
        ("5.1.0", ["2.7.10"]),
        ("5.1.1", ["2.7.10"]),
        ("5.1.2", ["2.7.10"]),
        ("5.3.0", ["2.7.10"]),
        ("5.3.1", ["2.7.10"]),
        ("5.4.0", ["2.7.10"]),
        ("5.4.1", ["2.7.10"]),
        ("5.6.0", ["2.7.12"]),
        ("5.7.0", ["2.7.13", "3.5.2"]),
        ("5.7.1", ["2.7.13", "3.5.2"]),
        ("5.8.0", ["2.7.13", "3.5.3"]),
        ("5.9.0", ["2.7.13", "3.5.3"]),
        ("5.10.0", ["2.7.13", "3.5.3"]),
        ("5.10.1", ["3.5.3"]),
        ("6.0.0", ["2.7.13", "3.5.3"]),
        ("7.0.0", ["2.7.13", "3.6.1"]),
        ("7.1.0", ["2.7.13", "3.5.3", "3.6.1"]),
        ("7.1.1", ["2.7.13", "3.6.1"]),
        ("7.2.0", ["2.7.13", "3.6.9"]),
        ("7.3.0", ["2.7.13", "3.6.9"]),
        ("7.3.1", ["2.7.13", "3.6.9"]),
        ("7.3.2", ["2.7.13", "3.6.9", "3.7.4"]),
        ("7.3.3", ["2.7.18", "3.6.12", "3.7.9"]),
        ("7.3.4", ["2.7.18", "3.7.10"]),
        ("7.3.5", ["2.7.18", "3.7.10"]),
        ("7.3.6", ["2.7.18", "3.7.12", "3.8.12"]),
        ("7.3.7", ["3.7.12", "3.8.12"]),
    ],
)
def test_supports_cpython(
    pypyinfo: PyPyVersionInfo, version: str, cpythons: List[str]
) -> None:
    assert pypyinfo.supports_cpython(version) == cpythons


@pytest.mark.parametrize("v", INVALID_VERSIONS + ["7.3", "7"])
def test_supports_cpython_invalid(pypyinfo: PyPyVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pypyinfo.supports_cpython(v)
    assert str(excinfo.value) == f"Invalid micro version: {v!r}"


@pytest.mark.parametrize("v", ["0.8.0", "1.5.0", "3.0.0", "7.4.0", "8.0.0"])
def test_supports_cpython_unknown(pypyinfo: PyPyVersionInfo, v: str) -> None:
    with pytest.raises(UnknownVersionError) as excinfo:
        pypyinfo.supports_cpython(v)
    assert str(excinfo.value) == f"Unknown version: {v!r}"
    assert excinfo.value.version == v


@pytest.mark.parametrize(
    "version,series",
    [
        ("7.3.5", ["2.7", "3.7"]),
        ("7.3", ["2.7", "3.6", "3.7", "3.8"]),
        ("7", ["2.7", "3.5", "3.6", "3.7", "3.8"]),
    ],
)
def test_supports_cpython_series(
    pypyinfo: PyPyVersionInfo, version: str, series: List[str]
) -> None:
    assert pypyinfo.supports_cpython_series(version) == series


@pytest.mark.parametrize("v", INVALID_VERSIONS)
def test_supports_cpython_series_invalid(pypyinfo: PyPyVersionInfo, v: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        pypyinfo.supports_cpython_series(v)
    assert str(excinfo.value) == f"Invalid version string: {v!r}"


@pytest.mark.parametrize("v", ["0.8", "1.5", "3", "7.3.9", "8.0.0"])
def test_supports_cpython_series_unknown(pypyinfo: PyPyVersionInfo, v: str) -> None:
    with pytest.raises(UnknownVersionError) as excinfo:
        pypyinfo.supports_cpython_series(v)
    assert str(excinfo.value) == f"Unknown version: {v!r}"
    assert excinfo.value.version == v

import pytest
from pyversion_info.util import MajorVersion, MicroVersion, MinorVersion


@pytest.mark.parametrize(
    "vstr,x",
    [
        ("3", 3),
        ("4", 4),
        ("10", 10),
    ],
)
def test_major_version(vstr: str, x: int) -> None:
    v = MajorVersion.parse(vstr)
    assert v == vstr
    assert str(v) == vstr
    assert repr(v) == f"MajorVersion({vstr!r})"
    assert v.x == x
    assert v.parts == (x,)
    assert MajorVersion.construct(x) == v


def test_major_version_cmp() -> None:
    VERSIONS = list(map(MajorVersion.parse, ["2", "3", "10"]))
    for i in range(len(VERSIONS) - 1):
        assert VERSIONS[i] == VERSIONS[i]
        assert VERSIONS[i] >= VERSIONS[i]
        assert VERSIONS[i] <= VERSIONS[i]
        assert VERSIONS[i] != VERSIONS[i + 1]
        assert VERSIONS[i] < VERSIONS[i + 1]
        assert VERSIONS[i + 1] > VERSIONS[i]
        assert VERSIONS[i] <= VERSIONS[i + 1]
        assert VERSIONS[i + 1] >= VERSIONS[i]


@pytest.mark.parametrize(
    "vstr,x,y",
    [
        ("3.0", 3, 0),
        ("3.6", 3, 6),
        ("3.10", 3, 10),
    ],
)
def test_minor_version(vstr: str, x: int, y: int) -> None:
    v = MinorVersion.parse(vstr)
    assert v == vstr
    assert str(v) == vstr
    assert repr(v) == f"MinorVersion({vstr!r})"
    assert v.x == x
    assert v.y == y
    assert v.parts == (x, y)
    assert MinorVersion.construct(x, y) == v


def test_minor_version_cmp() -> None:
    VERSIONS = list(map(MinorVersion.parse, ["2.0", "2.7", "3.0", "3.6", "3.10"]))
    for i in range(len(VERSIONS) - 1):
        assert VERSIONS[i] == VERSIONS[i]
        assert VERSIONS[i] >= VERSIONS[i]
        assert VERSIONS[i] <= VERSIONS[i]
        assert VERSIONS[i] != VERSIONS[i + 1]
        assert VERSIONS[i] < VERSIONS[i + 1]
        assert VERSIONS[i + 1] > VERSIONS[i]
        assert VERSIONS[i] <= VERSIONS[i + 1]
        assert VERSIONS[i + 1] >= VERSIONS[i]


@pytest.mark.parametrize(
    "vstr,x,y,z,minor",
    [
        ("3.0.1", 3, 0, 1, "3.0"),
        ("3.6.10", 3, 6, 10, "3.6"),
        ("3.10.7", 3, 10, 7, "3.10"),
    ],
)
def test_micro_version(vstr: str, x: int, y: int, z: int, minor: str) -> None:
    v = MicroVersion.parse(vstr)
    assert v == vstr
    assert str(v) == vstr
    assert repr(v) == f"MicroVersion({vstr!r})"
    assert v.x == x
    assert v.y == y
    assert v.z == z
    assert v.parts == (x, y, z)
    assert MicroVersion.construct(x, y, z) == v
    assert v.minor == MinorVersion.parse(minor)


def test_micro_version_cmp() -> None:
    VERSIONS = list(
        map(
            MicroVersion.parse,
            ["2.0.1", "2.1.0", "2.7.5", "3.1.3", "3.6.0", "3.6.2", "3.6.10", "3.10.0"],
        )
    )
    for i in range(len(VERSIONS) - 1):
        assert VERSIONS[i] == VERSIONS[i]
        assert VERSIONS[i] >= VERSIONS[i]
        assert VERSIONS[i] <= VERSIONS[i]
        assert VERSIONS[i] != VERSIONS[i + 1]
        assert VERSIONS[i] < VERSIONS[i + 1]
        assert VERSIONS[i + 1] > VERSIONS[i]
        assert VERSIONS[i] <= VERSIONS[i + 1]
        assert VERSIONS[i + 1] >= VERSIONS[i]

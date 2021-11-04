from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date, datetime
import re
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type, TypeVar, Union
from pydantic import BaseModel, parse_obj_as
from pydantic.validators import str_validator

if TYPE_CHECKING:
    from pydantic.typing import CallableGenerator

V = TypeVar("V", bound="Version")


class Version(ABC):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        yield str_validator
        yield cls._validate
        yield cls

    @classmethod
    @abstractmethod
    def _validate(cls, s: str) -> str:
        ...

    @classmethod
    def parse(cls: Type[V], s: Any) -> V:
        return parse_obj_as(cls, s)

    @property
    @abstractmethod
    def parts(self) -> Tuple[int, ...]:
        ...

    def __repr__(self) -> str:
        return f"{type(self).__name__}({super().__repr__()})"

    # Using functools.total_ordering to derive everything from __lt__ doesn't
    # work, as the comparison operators inherited from str keep the decorator
    # from working.

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.parts < other.parts
        else:
            return NotImplemented  # pragma: no cover

    def __le__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.parts <= other.parts
        else:
            return NotImplemented  # pragma: no cover

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.parts > other.parts
        else:
            return NotImplemented  # pragma: no cover

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.parts >= other.parts
        else:
            return NotImplemented  # pragma: no cover


class MajorVersion(Version, str):
    x: int

    def __init__(self, s: str) -> None:
        self.x = int(s)

    @classmethod
    def _validate(cls, s: str) -> str:
        if re.fullmatch(r"(\d+)", s):
            return s
        else:
            raise ValueError(f"Invalid major version: {s!r}")

    @property
    def parts(self) -> Tuple[int]:
        return (self.x,)

    @classmethod
    def construct(cls, x: int) -> MajorVersion:
        return cls.parse(str(x))


class MinorVersion(Version, str):
    x: int
    y: int

    def __init__(self, s: str) -> None:
        x, _, y = s.partition(".")
        self.x = int(x)
        self.y = int(y)

    @classmethod
    def _validate(cls, s: str) -> str:
        if re.fullmatch(r"(\d+)\.(\d+)", s):
            return s
        else:
            raise ValueError(f"Invalid minor version: {s!r}")

    @property
    def parts(self) -> Tuple[int, int]:
        return (self.x, self.y)

    @classmethod
    def construct(cls, x: int, y: int) -> MinorVersion:
        return cls.parse(f"{x}.{y}")


class MicroVersion(Version, str):
    x: int
    y: int
    z: int

    def __init__(self, s: str) -> None:
        x, y, z = s.split(".")
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    @classmethod
    def _validate(cls, s: str) -> str:
        if re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", s):
            return s
        else:
            raise ValueError(f"Invalid micro version: {s!r}")

    @property
    def parts(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)

    @classmethod
    def construct(cls, x: int, y: int, z: int) -> MicroVersion:
        return cls.parse(f"{x}.{y}.{z}")

    @property
    def minor(self) -> MinorVersion:
        return MinorVersion.construct(self.x, self.y)


# Union[bool, date] needs to have `bool` first so that True and False aren't
# treated as the timestamps 1 and 0.


class RawCPythonInfo(BaseModel):
    release_dates: Dict[MicroVersion, Union[bool, date]]
    eol_dates: Dict[MinorVersion, Union[bool, date]]


class RawPyPyInfo(BaseModel):
    release_dates: Dict[MicroVersion, Union[bool, date]]
    cpython_versions: Dict[MicroVersion, List[MicroVersion]]


class RawDatabase(BaseModel):
    last_modified: datetime
    cpython: RawCPythonInfo
    pypy: RawPyPyInfo

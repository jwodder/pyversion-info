from __future__ import annotations
import argparse
from dataclasses import dataclass
from datetime import date
from enum import Enum
from functools import partial
import json
import sys
from typing import Any, Protocol
from . import (
    CPythonVersionInfo,
    PyPyVersionInfo,
    VersionDatabase,
    VersionInfo,
    __version__,
    parse_version,
)
from .util import MajorVersion, MicroVersion, MinorVersion


class Subcommand(Protocol):
    def run(self, vd: VersionDatabase) -> int: ...


@dataclass
class Command:
    database: str | None
    subcommand: Subcommand

    @classmethod
    def from_args(cls, argv: list[str] | None = None) -> Command:
        parser = argparse.ArgumentParser(
            description=(
                "Show details about Python versions\n"
                "\n"
                "Visit <https://github.com/jwodder/pyversion-info> for more information."
            ),
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "-d",
            "--database",
            metavar="FILE|URL",
            help="Fetch version information from the given database",
        )
        parser.add_argument(
            "-V", "--version", action="version", version=f"%(prog)s {__version__}"
        )

        subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

        listparser = subparsers.add_parser(
            "list", help="List known versions at the given version level"
        )
        listparser.add_argument(
            "-a",
            "--all",
            dest="mode",
            action="store_const",
            const=Mode.ALL,
            help="List all known versions",
            # This goes on the first option with `dest="mode"`:
            default=Mode.RELEASED,
        )
        listparser.add_argument(
            "--cpython",
            dest="py",
            action="store_const",
            const=PyImpl.CPYTHON,
            help="Show information about CPython versions  [default]",
            default=PyImpl.CPYTHON,
        )
        listparser.add_argument(
            "-n",
            "--not-eol",
            dest="mode",
            action="store_const",
            const=Mode.NOT_EOL,
            help="List only versions that are not EOL (supported versions + unreleased versions)",
        )
        listparser.add_argument(
            "--pypy",
            dest="py",
            action="store_const",
            const=PyImpl.PYPY,
            help="Show information about PyPy versions",
        )
        listparser.add_argument(
            "-r",
            "--released",
            dest="mode",
            action="store_const",
            const=Mode.RELEASED,
            help="List only released versions  [default]",
        )
        listparser.add_argument(
            "-s",
            "--supported",
            dest="mode",
            action="store_const",
            const=Mode.SUPPORTED,
            help="List only supported versions",
        )
        # Don't convert with `type` here, as that takes effect before `choices`
        listparser.add_argument("level", choices=["major", "minor", "micro"])

        showparser = subparsers.add_parser(
            "show", help="Show information about a Python version"
        )
        showparser.add_argument(
            "--cpython",
            dest="py",
            action="store_const",
            const=PyImpl.CPYTHON,
            help="Show information about CPython versions  [default]",
            default=PyImpl.CPYTHON,
        )
        showparser.add_argument("-J", "--json", action="store_true", help="Output JSON")
        showparser.add_argument(
            "--pypy",
            dest="py",
            action="store_const",
            const=PyImpl.PYPY,
            help="Show information about PyPy versions",
        )
        showparser.add_argument(
            "-S",
            "--subversions",
            # Don't convert with `type` here, as that takes effect before `choices`
            choices=["all", "not-eol", "released", "supported"],
            help="Which subversions to list  [default: released]",
            default="released",
        )
        showparser.add_argument("version")

        args = parser.parse_args(argv)
        subcommand: Subcommand
        match args.subcommand:
            case "list":
                subcommand = ListCommand(
                    level=Level(args.level), mode=args.mode, py=args.py
                )
            case "show":
                subcommand = ShowCommand(
                    version=args.version,
                    subversions=Mode(args.subversions),
                    json=args.json,
                    py=args.py,
                )
            case cmd:  # pragma: no cover
                raise AssertionError(f"Unexpected subcommand: {cmd!r}")
        return Command(database=args.database, subcommand=subcommand)

    def run(self) -> int:
        if self.database is None:
            vd = VersionDatabase.fetch()
        elif self.database.lower().startswith(("http://", "https://")):
            vd = VersionDatabase.fetch(self.database)
        else:
            vd = VersionDatabase.parse_file(self.database)
        try:
            return self.subcommand.run(vd)
        except ValueError as e:
            print(f"pyversion-info: {e}", file=sys.stderr)
            return 1


class PyImpl(Enum):
    CPYTHON = 0
    PYPY = 1

    def get_info(self, vd: VersionDatabase) -> VersionInfo:
        match self:
            case PyImpl.CPYTHON:
                return vd.cpython
            case PyImpl.PYPY:
                return vd.pypy
            case _:  # pragma: no cover
                raise AssertionError(f"Unexpected Python implementation: {self!r}")


class Mode(Enum):
    ALL = "all"
    NOT_EOL = "not-eol"
    RELEASED = "released"
    SUPPORTED = "supported"

    def filter_versions(self, info: VersionInfo, versions: list[str]) -> list[str]:
        match self:
            case Mode.ALL:
                filterer = yes
            case Mode.RELEASED:
                filterer = info.is_released
            case Mode.SUPPORTED:
                if not isinstance(info, CPythonVersionInfo):
                    raise ValueError('"supported" only applies to CPython versions')
                filterer = info.is_supported
            case Mode.NOT_EOL:
                if not isinstance(info, CPythonVersionInfo):
                    raise ValueError('"not-eol" only applies to CPython versions')
                filterer = partial(is_not_eol, info)
            case mode:  # pragma: no cover
                raise AssertionError(f"Unexpected mode: {mode!r}")
        return list(filter(filterer, versions))


class Level(Enum):
    MAJOR = "major"
    MINOR = "minor"
    MICRO = "micro"

    def get_versions(self, info: VersionInfo) -> list[str]:
        match self:
            case Level.MAJOR:
                return info.major_versions()
            case Level.MINOR:
                return info.minor_versions()
            case Level.MICRO:
                return info.micro_versions()
            case level:  # pragma: no cover
                raise AssertionError(f"Unexpected level: {level!r}")


@dataclass
class ListCommand:
    level: Level
    mode: Mode
    py: PyImpl

    def run(self, vd: VersionDatabase) -> int:
        info = self.py.get_info(vd)
        for v in self.mode.filter_versions(info, self.level.get_versions(info)):
            print(v)
        return 0


@dataclass
class ShowCommand:
    version: str
    subversions: Mode
    json: bool
    py: PyImpl

    def run(self, vd: VersionDatabase) -> int:
        info = self.py.get_info(vd)
        v = parse_version(self.version)
        data: list[tuple[str, str, Any]] = [
            ("version", "Version", str(v)),
            # ("level", "Level", ---),
            ("release_date", "Release-Date", info.release_date(v)),
            ("is_released", "Is-Released", info.is_released(v)),
        ]
        if isinstance(info, CPythonVersionInfo):
            data.append(("is_supported", "Is-Supported", info.is_supported(v)))
        if isinstance(v, MajorVersion):
            data.insert(1, ("level", "Level", "major"))
            if isinstance(info, CPythonVersionInfo):
                data.append(("eol_date", "EOL-Date", info.eol_date(v)))
                data.append(("is_eol", "Is-EOL", info.is_eol(v)))
            data.append(
                (
                    "subversions",
                    "Subversions",
                    self.subversions.filter_versions(info, info.subversions(v)),
                )
            )
            if isinstance(info, PyPyVersionInfo):
                data.append(
                    (
                        "cpython_series",
                        "CPython-Series",
                        info.supported_cpython_series(
                            v,
                            released=self.subversions is Mode.RELEASED,
                        ),
                    )
                )
        elif isinstance(v, MinorVersion):
            data.insert(1, ("level", "Level", "minor"))
            if isinstance(info, CPythonVersionInfo):
                data.append(("eol_date", "EOL-Date", info.eol_date(v)))
                data.append(("is_eol", "Is-EOL", info.is_eol(v)))
            data.append(
                (
                    "subversions",
                    "Subversions",
                    self.subversions.filter_versions(info, info.subversions(v)),
                )
            )
            if isinstance(info, PyPyVersionInfo):
                data.append(
                    (
                        "cpython_series",
                        "CPython-Series",
                        info.supported_cpython_series(
                            v,
                            released=self.subversions is Mode.RELEASED,
                        ),
                    )
                )
        else:
            assert isinstance(v, MicroVersion)
            data.insert(1, ("level", "Level", "micro"))
            if isinstance(info, CPythonVersionInfo):
                data.append(("eol_date", "EOL-Date", info.eol_date(v)))
                data.append(("is_eol", "Is-EOL", info.is_eol(v)))
            if isinstance(info, PyPyVersionInfo):
                data.append(("cpython", "CPython", info.supported_cpython(v)))
        if self.json:
            print(json.dumps({k: v for k, _, v in data}, indent=4, default=str))
        else:
            for _, label, val in data:
                if isinstance(val, date):
                    val = str(val)
                elif isinstance(val, bool):
                    val = "yes" if val else "no"
                elif isinstance(val, list):
                    val = ", ".join(val)
                elif val is None:
                    val = "UNKNOWN"
                print(f"{label}: {val}")
        return 0


def main(argv: list[str] | None = None) -> int:
    return Command.from_args(argv).run()


def is_not_eol(pyvinfo: CPythonVersionInfo, version: str) -> bool:
    return not pyvinfo.is_eol(version)


def yes(version: str) -> bool:  # noqa: U100
    return True


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

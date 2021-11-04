from datetime import date
from functools import partial, wraps
import json
from typing import Any, Callable, List, Optional, Tuple
import click
from . import (
    CPythonVersionInfo,
    PyPyVersionInfo,
    VersionDatabase,
    VersionInfo,
    __version__,
    parse_version,
    unparse_version,
)


def map_exc_to_click(func: Callable) -> Callable:
    @wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            raise click.UsageError(str(e))

    return wrapped


@click.group()
@click.version_option(
    __version__,
    "-V",
    "--version",
    message="%(prog)s %(version)s",
)
@click.option(
    "-d",
    "--database",
    metavar="FILE|URL",
    help="Fetch version information from the given database",
)
@click.pass_context
def main(ctx: click.Context, database: Optional[str]) -> None:
    """Show details about Python versions"""
    if database is None:
        ctx.obj = VersionDatabase.fetch()
    elif database.lower().startswith(("http://", "https://")):
        ctx.obj = VersionDatabase.fetch(database)
    else:
        ctx.obj = VersionDatabase.parse_file(database)


@main.command("list")
@click.option("-a", "--all", "mode", flag_value="all", help="List all known versions")
@click.option(
    "--cpython",
    "py",
    flag_value="cpython",
    help="Show information about CPython versions  [default]",
    default=True,
)
@click.option(
    "-n",
    "--not-eol",
    "mode",
    flag_value="not-eol",
    help="List only versions that are not EOL (supported versions + unreleased versions)",
)
@click.option(
    "--pypy",
    "py",
    flag_value="pypy",
    help="Show information about PyPy versions",
)
@click.option(
    "-r",
    "--released",
    "mode",
    flag_value="released",
    help="List only released versions  [default]",
    default=True,
)
@click.option(
    "-s",
    "--supported",
    "mode",
    flag_value="supported",
    help="List only supported versions",
)
@click.argument("level", type=click.Choice(["major", "minor", "micro"]))
@click.pass_obj
@map_exc_to_click
def list_cmd(vd: VersionDatabase, level: str, mode: str, py: str) -> None:
    """List known versions at the given version level"""
    info = vd.pypy if py == "pypy" else vd.cpython
    func = {
        "major": info.major_versions,
        "minor": info.minor_versions,
        "micro": info.micro_versions,
    }[level]
    for v in filter_versions(mode, info, func()):
        print(v)


@main.command()
@click.option(
    "--cpython",
    "py",
    flag_value="cpython",
    help="Show information about CPython versions  [default]",
    default=True,
)
@click.option("-J", "--json", "do_json", is_flag=True, help="Output JSON")
@click.option(
    "--pypy",
    "py",
    flag_value="pypy",
    help="Show information about PyPy versions",
)
@click.option(
    "-S",
    "--subversions",
    type=click.Choice(["all", "not-eol", "released", "supported"]),
    help="Which subversions to list",
    default="released",
    show_default=True,
)
@click.argument("version")
@click.pass_obj
@map_exc_to_click
def show(
    vd: VersionDatabase, version: str, subversions: str, do_json: bool, py: str
) -> None:
    """Show information about a Python version"""
    info = vd.pypy if py == "pypy" else vd.cpython
    v = parse_version(version)
    data: List[Tuple[str, str, Any]] = [
        ("version", "Version", unparse_version(v)),
        # ("level", "Level", ---),
        ("release_date", "Release-Date", info.release_date(version)),
        ("is_released", "Is-Released", info.is_released(version)),
    ]
    if isinstance(info, CPythonVersionInfo):
        data.append(("is_supported", "Is-Supported", info.is_supported(version)))
    if len(v) == 1:
        data.insert(1, ("level", "Level", "major"))
        data.append(
            (
                "subversions",
                "Subversions",
                filter_versions(subversions, info, info.subversions(version)),
            )
        )
        if isinstance(info, PyPyVersionInfo):
            data.append(
                (
                    "cpython_series",
                    "CPython-Series",
                    info.supports_cpython_series(
                        version, released=subversions == "released"
                    ),
                )
            )
    elif len(v) == 2:
        data.insert(1, ("level", "Level", "minor"))
        if isinstance(info, CPythonVersionInfo):
            data.append(("eol_date", "EOL-Date", info.eol_date(version)))
            data.append(("is_eol", "Is-EOL", info.is_eol(version)))
        data.append(
            (
                "subversions",
                "Subversions",
                filter_versions(subversions, info, info.subversions(version)),
            )
        )
        if isinstance(info, PyPyVersionInfo):
            data.append(
                (
                    "cpython_series",
                    "CPython-Series",
                    info.supports_cpython_series(
                        version, released=subversions == "released"
                    ),
                )
            )
    else:
        data.insert(1, ("level", "Level", "micro"))
        if isinstance(info, PyPyVersionInfo):
            data.append(("cpython", "CPython", info.supports_cpython(version)))
    if do_json:
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


def is_not_eol(pyvinfo: CPythonVersionInfo, version: str) -> bool:
    v = parse_version(version)
    if len(v) == 1:
        return not all(map(pyvinfo.is_eol, pyvinfo.subversions(version)))
    elif len(v) == 2:
        return not pyvinfo.is_eol(version)
    else:
        x, y, _ = v
        return not pyvinfo.is_eol(unparse_version((x, y)))


def yes(version: str) -> bool:  # noqa: U100
    return True


def filter_versions(mode: str, info: VersionInfo, versions: List[str]) -> List[str]:
    if mode == "all":
        filterer = yes
    elif mode == "released":
        filterer = info.is_released
    elif mode == "supported":
        if not isinstance(info, CPythonVersionInfo):
            raise click.UsageError("'supported' only applies to CPython versions")
        filterer = info.is_supported
    elif mode == "not-eol":
        if not isinstance(info, CPythonVersionInfo):
            raise click.UsageError("'not-eol' only applies to CPython versions")
        filterer = partial(is_not_eol, info)
    else:
        raise AssertionError(f"Unexpected mode: {mode!r}")  # pragma: no cover
    return list(filter(filterer, versions))


if __name__ == "__main__":
    main()  # pragma: no cover

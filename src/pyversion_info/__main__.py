from datetime import date
from functools import partial, wraps
import json
import re
from typing import Any, Callable, Dict, Iterator, List, Optional
import click
from . import (
    PyVersionInfo,
    __version__,
    get_pyversion_info,
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
        ctx.obj = get_pyversion_info()
    elif database.lower().startswith(("http://", "https://")):
        ctx.obj = get_pyversion_info(database)
    else:
        with open(database, "rb") as fp:
            ctx.obj = PyVersionInfo(json.load(fp))


@main.command("list")
@click.option("-a", "--all", "mode", flag_value="all", help="List all known versions")
@click.option(
    "-n",
    "--not-eol",
    "mode",
    flag_value="not-eol",
    help="List only versions that are not EOL (supported versions + unreleased versions)",
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
def list_cmd(pyvinfo: PyVersionInfo, level: str, mode: str) -> None:
    """List known versions at the given version level"""
    func = {
        "major": pyvinfo.major_versions,
        "minor": pyvinfo.minor_versions,
        "micro": pyvinfo.micro_versions,
    }[level]
    for v in filter_versions(mode, pyvinfo, func()):
        print(v)


@main.command()
@click.option("-J", "--json", "do_json", is_flag=True, help="Output JSON")
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
def show(pyvinfo: PyVersionInfo, version: str, subversions: str, do_json: bool) -> None:
    """Show information about a Python version"""
    v = parse_version(version)
    data: Dict[str, Any] = {
        "version": unparse_version(v),
        "level": None,  # So it will show up on line 2
        "release_date": pyvinfo.release_date(version),
        "is_released": pyvinfo.is_released(version),
        "is_supported": pyvinfo.is_supported(version),
    }
    if len(v) == 1:
        data["level"] = "major"
        data["subversions"] = list(
            filter_versions(subversions, pyvinfo, pyvinfo.subversions(version))
        )
    elif len(v) == 2:
        data["level"] = "minor"
        data["eol_date"] = pyvinfo.eol_date(version)
        data["is_eol"] = pyvinfo.is_eol(version)
        data["subversions"] = list(
            filter_versions(subversions, pyvinfo, pyvinfo.subversions(version))
        )
    else:
        data["level"] = "micro"
    if do_json:
        print(json.dumps(data, indent=4, default=str))
    else:
        for k, val in data.items():
            label = re.sub(r"[Ee]ol", "EOL", k.replace("_", "-").capitalize())
            if k in ("release_date", "eol_date"):
                if isinstance(val, date):
                    val = str(val)
                else:
                    val = "UNKNOWN"
            elif isinstance(val, bool):
                val = "yes" if val else "no"
            elif isinstance(val, list):
                val = ", ".join(val)
            print(f"{label}: {val}")


def is_not_eol(pyvinfo: PyVersionInfo, version: str) -> bool:
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


def filter_versions(
    mode: str, pyvinfo: PyVersionInfo, versions: List[str]
) -> Iterator[str]:
    if mode == "all":
        filterer = yes
    elif mode == "released":
        filterer = pyvinfo.is_released
    elif mode == "supported":
        filterer = pyvinfo.is_supported
    elif mode == "not-eol":
        filterer = partial(is_not_eol, pyvinfo)
    else:
        raise AssertionError(f"Unexpected mode: {mode!r}")  # pragma: no cover
    return filter(filterer, versions)


if __name__ == "__main__":
    main()  # pragma: no cover

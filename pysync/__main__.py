import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, NamedTuple, cast

import typer
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from rich.console import Console

type ParsedArgs = tuple[Path, list[str]]

__version__ = "0.3.7"

app = typer.Typer()
console = Console()


class VersionSpecifiers(str, Enum):
    """Package version specifiers, see https://packaging.python.org/en/latest/specifications/version-specifiers/#id5"""

    COMPATIBLE = "~="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="


class Dependency(NamedTuple):
    name: str
    string: str
    specifiers: SpecifierSet


@dataclass
class DependencyMap:
    outdated: list[str] = field(default_factory=list)
    dependency_names: set[str] = field(default_factory=set)
    root_dependencies: list[Dependency] = field(default_factory=list)
    additional_dependencies: defaultdict[str, list[Dependency]] = field(default_factory=lambda: defaultdict(list))

    # Regex for Python package names, see https://packaging.python.org/en/latest/specifications/name-normalization/
    # This pattern also adds matching for optional extras, i.e. gunicorn[gevent]
    _PACKAGE_NAME_REGEX = r"^([A-Z0-9](?:[A-Z0-9._-]*[A-Z0-9])?)(\[[A-Z0-9]+(?:,[A-Z0-9]+)*\])?"

    def add_dependency(self, raw_dependency: str, group: str | None = None) -> None:
        dependency = self._get_dependency_info(raw_dependency)
        self.dependency_names.add(dependency.name)
        if group:
            self.additional_dependencies[group].append(dependency)
        else:
            self.root_dependencies.append(dependency)

    def _get_dependency_info(self, dependency: str) -> Dependency:
        """Get detailed information about a specific dependency"""
        match = re.search(self._PACKAGE_NAME_REGEX, dependency, re.IGNORECASE)
        if not match:
            console.print(f"[red]Failed to parse {dependency}, invalid package name")
            raise typer.Exit(1)
        version_specifiers = str(dependency[match.end() :])  # Trim package name
        return Dependency(name=match.group(1), string=dependency, specifiers=SpecifierSet(version_specifiers))


def get_dependencies(pyproject: dict[str, Any]) -> DependencyMap:
    """Get a list of top-level project dependencies"""
    dependency_map = DependencyMap()
    # Add root-level dependencies
    for dependency in pyproject["project"]["dependencies"]:
        dependency_map.add_dependency(dependency)
    # Add dependencies from dependency groups
    for group, dependencies in pyproject.get("dependency-groups", {}).items():
        for dependency in dependencies:
            dependency_map.add_dependency(dependency, group)
    return dependency_map


def get_synced_dependency_version(dependency: Dependency, package_version: Version, updates: list[str]) -> str:
    if not dependency.specifiers:
        console.print(f"[red]- WARNING {dependency.name} has no version specifiers, pinning to >={package_version}")
        updates.append(dependency.string)  # Add to list of updated dependencies
        return f"{dependency.name}>={package_version}"  # Missing specifiers, pin to >= current version

    for specifier in dependency.specifiers:
        if Version(specifier.version) == package_version:
            continue  # Version is already up to date
        if specifier.operator in [VersionSpecifiers.GREATER_THAN, VersionSpecifiers.GREATER_THAN_OR_EQUAL]:
            console.print(f"- Bumping {dependency.name} from {specifier} to >={package_version}")
            updates.append(dependency.string)  # Add to list of updated dependencies
            return dependency.string.replace(str(specifier), f">={package_version}")  # Replace returns a copy
        elif specifier.operator is VersionSpecifiers.COMPATIBLE:  # TODO: Support this
            console.print(f"[red]- WARNING {specifier.operator} is not supported, skipping {dependency.specifiers}")

    return dependency.string  # Nothing to update


def sync_dependencies(workdir: Path) -> bool:
    """Sync pyproject.toml dependency versions with versions in the uv.lock file"""
    with Path(workdir, "pyproject.toml").open("r") as f:
        pyproject_raw = f.readlines()  # Read file as raw text
    with Path(workdir, "pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)
    with Path(workdir, "uv.lock").open("rb") as f:
        packages = tomllib.load(f)["package"]  # Get a list of packages from the lockfile

    # Get direct project dependencies and corresponding top-level packages from all dependency groups
    dependency_map = get_dependencies(pyproject)
    top_level_packages = {
        package["name"]: Version(package["version"])
        for package in packages
        if package["name"] in dependency_map.dependency_names
    }
    console.print(
        f"[bold cyan]\nSyncing dependency versions...[/]\n"
        f"Found {len(top_level_packages)} top-level packages ({len(packages)} total)",
        highlight=False,
    )

    # Merged list of dependencies  # TODO: Optimize this
    dependencies = [dep for group_dep in dependency_map.additional_dependencies.values() for dep in group_dep]
    dependencies.extend(dependency_map.root_dependencies)
    updates: list[str] = []  # List of updated dependencies

    # Bump dependency specifiers for root-level dependencies and dependencies in dependency groups
    for dependency in dependencies:
        dependency_pattern = rf"^ *\"{re.escape(dependency.string)}[~=!<\"]"  # TODO: Handle single-line dep list
        for line_num, line in enumerate(pyproject_raw):
            if re.search(dependency_pattern, line):
                pyproject_raw[line_num] = line.replace(
                    dependency.string,
                    get_synced_dependency_version(dependency, top_level_packages[dependency.name], updates),
                )
                break
        else:
            console.print(f"[red]Failed to find dependency for package '{dependency.name}' in pyproject.toml")

    # Write updated pyproject.toml, write as raw lines to preserve formatting and comments
    with Path(workdir, "pyproject.toml").open("w", newline="") as f:
        f.writelines(pyproject_raw)

    console.print(f"[bold green]Updated {len(updates)} dependencies")
    return bool(updates)  # Indicate whether any dependencies were changed


def uv_sync(workdir: Path, uv_command: list[str]) -> None:
    try:
        subprocess.run(uv_command, cwd=workdir, check=True, stdout=sys.stdout, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]'{' '.join(e.cmd)}' failed with non-zero exit status {e.returncode} (workdir={workdir})")
        raise typer.Exit(e.returncode) from None


def args_cb(arg_1: str) -> ParsedArgs:
    """Set default workdir and ensure pyproject.toml and uv.lock files exist in the given working directory"""
    workdir = Path(arg_1)  # Covert to a Path, func arg must be a str for Typer to allow returning a tuple

    # Handle arbitrary args (intended for uv) being misinterpreted as workdir (if called with no explicit workdir arg)
    if workdir.exists():
        uv_passthrough_arg = []  # No additional args to pass through
        workdir = workdir.parent.resolve() if workdir.is_file() else workdir.resolve()  # Get absolute path
    elif str(workdir).startswith("-"):
        uv_passthrough_arg = [str(workdir)]  # First arg should be passed through to uv (ex: -U or --upgrade)
        workdir = Path.cwd()  # Use current dir as Path.cwd from arg default factory was not invoked
    else:
        raise typer.BadParameter(f"Path '{workdir.resolve()}' does not exist")

    # Ensure pyproject.toml and uv.lock files exist in the target workdir
    if not Path(workdir, "pyproject.toml").exists():
        raise typer.BadParameter(f"pyproject.toml not found in workdir: {workdir}")
    if not Path(workdir, "uv.lock").exists():
        raise typer.BadParameter(f"uv.lock not found in workdir: {workdir}")

    return workdir, uv_passthrough_arg


def version_cb(value: bool) -> None:
    if value:
        console.print(f"pysync {__version__}")
        raise typer.Exit()


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def sync(
    ctx: typer.Context,
    args: Annotated[str, typer.Argument(callback=args_cb, default_factory=Path.cwd)],
    version: Annotated[bool | None, typer.Option("--version", callback=version_cb, is_eager=True)] = None,
) -> None:
    """Sync minimum dependency versions of the pyproject.toml and uv.lock files"""
    workdir, initial_arg = cast(ParsedArgs, args)

    # Call 'uv sync' as a subprocess to update lockfile
    uv_command = ["uv", "sync"] + initial_arg + ctx.args  # Build uv command
    console.print(f"Running [bold cyan]{' '.join(uv_command)}")  # Print uv command
    uv_sync(workdir, uv_command)

    # Sync dependencies, re-locking if there are any changes
    if sync_dependencies(workdir):
        console.print(f"\n[bold cyan]Dependencies changed, re-running {' '.join(uv_command)}")
        uv_sync(workdir, uv_command)


if __name__ == "__main__":
    app()  # Support calling via python -m (as a module)

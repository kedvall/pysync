import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, NamedTuple

import tomli
import tomli_w
import typer
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from rich.console import Console

from pysync.uv import uv_sync

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
    _PACKAGE_NAME_REGEX = r"^([A-Z0-9][A-Z0-9._-]*[A-Z0-9]|[A-Z0-9])"

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
        return Dependency(name=match[0], string=dependency, specifiers=SpecifierSet(version_specifiers))


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


def get_synced_dependency(dependency: Dependency, package_version: Version, updates: list[str]) -> str:
    if not dependency.specifiers:
        console.print(f"[red]- WARNING {dependency.name} has no version specifiers, pinning to >={package_version}")
        updates.append(dependency.name)  # Add to the list of updated dependencies
        return f"{dependency.name}>={package_version}"  # Missing specifiers, pin to >= current version

    for specifier in dependency.specifiers:
        if Version(specifier.version) == package_version:
            continue  # Version is already up to date
        if specifier.operator in [VersionSpecifiers.GREATER_THAN, VersionSpecifiers.GREATER_THAN_OR_EQUAL]:
            console.print(f"- Bumping {dependency.name} from {specifier} to >={package_version}")
            updates.append(dependency.name)  # Add to the list of updated dependencies
            return dependency.string.replace(str(specifier), f">={package_version}")  # Replace returns a copy
        elif specifier.operator is VersionSpecifiers.COMPATIBLE:
            console.print(f"[red]- WARNING {specifier.operator} is not supported, skipping {dependency.specifiers}")

    return dependency.string  # Nothing to update


def sync_dependencies(workdir: Path) -> None:
    """Sync pyproject.toml dependency versions with versions in the uv.lock file"""
    with Path(workdir, "pyproject.toml").open("rb") as f:
        pyproject = tomli.load(f)
    with Path(workdir, "uv.lock").open("rb") as f:
        packages: list[dict[str, Any]] = tomli.load(f)["package"]  # Get dict of packages from lockfile

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

    # Bump dependency specifiers for root-level dependencies
    updates: list[str] = []  # List of updated dependencies
    pyproject["project"]["dependencies"] = [
        get_synced_dependency(dep, top_level_packages[dep.name], updates) for dep in dependency_map.root_dependencies
    ]
    # Bump dependency specifiers for dependencies in dependency groups
    pyproject["dependency-groups"] = {
        group: [get_synced_dependency(dep, top_level_packages[dep.name], updates) for dep in dependencies]
        for group, dependencies in dependency_map.additional_dependencies.items()
    }

    # Write updated pyproject.toml
    with Path(workdir, "test_pyproject.toml").open("wb") as file:
        tomli_w.dump(pyproject, file)

    console.print(f"[bold green]Updated {len(updates)} dependencies")


def workdir_callback(workdir_arg: Path) -> Path:
    """Ensure pyproject.toml and uv.lock files exist in the given working directory"""
    workdir = workdir_arg.parent if workdir_arg.is_file() else workdir_arg  # Get parent dir if called on a file
    if not Path(workdir, "pyproject.toml").exists():
        raise typer.BadParameter(f"pyproject.toml not found in workdir: {workdir}")
    if not Path(workdir, "uv.lock").exists():
        raise typer.BadParameter(f"uv.lock not found in workdir: {workdir}")
    return workdir.resolve()


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def sync(
    workdir: Annotated[
        Path,
        typer.Argument(exists=True, writable=True, callback=workdir_callback, default_factory=Path.cwd),
    ],
    uv_passthrough_args: Annotated[list[str] | None, typer.Argument()] = None,
) -> None:
    """Sync minimum dependency versions of the pyproject.toml and uv.lock files"""
    uv_sync(workdir, uv_passthrough_args)  # Call 'uv sync' as a subprocess to update lockfile
    sync_dependencies(workdir)
    uv_sync(workdir, uv_passthrough_args, silent=True)


if __name__ == "__main__":
    app()  # Support calling via python -m (as a module)

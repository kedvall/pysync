import re
import sys
from pathlib import Path
from enum import Enum
from typing import Any, NamedTuple

from packaging.specifiers import SpecifierSet, Specifier
from packaging.version import Version
import tomli

# Regex that matches Python package names from https://packaging.python.org/en/latest/specifications/name-normalization/
PACKAGE_NAME_REGEX = r"^([A-Z0-9][A-Z0-9._-]*[A-Z0-9]|[A-Z0-9])"


class Package(NamedTuple):
    name: str
    version: Version
    specifiers: SpecifierSet


class VersionSpecifierOperators(str, Enum):
    """
    Package version specifiers. Note that some are intentionally excluded as they are not handled/would not be changed.
    From https://packaging.python.org/en/latest/specifications/version-specifiers/#id5
    """

    COMPATIBLE = "~="
    MATCHING = "=="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="


SUPPORTED_OPERATORS = [operator.value for operator in VersionSpecifierOperators]


def get_workdir() -> Path:
    if len(sys.argv) < 2:
        return Path.cwd()
    workdir = Path(sys.argv[1]).resolve()
    if not workdir.exists():
        sys.exit(f"{workdir} not found, exiting...")
    elif workdir.is_file():
        workdir = workdir.parent
    return workdir


def load_toml_file(workdir: Path, filename: str) -> dict[str, Any]:
    """Loads a toml file from the given workdir, with error handling"""
    try:
        with Path(workdir, filename).open("rb") as file:
            return tomli.load(file)
    except FileNotFoundError:
        sys.exit(f"Failed to find {filename} file in {workdir}")


def get_dependency_group_deps(pyproject: dict[str, Any]) -> list[str]:
    """Get additional top-level dependencies from optional dependency groups (such as dev)"""
    dependencies: list[str] = []
    dependency_groups = pyproject.get("dependency-groups", {})
    for group in dependency_groups.values():
        dependencies.extend(group)
    return dependencies


def get_dependencies(pyproject: dict[str, Any]) -> dict[str, str]:
    """Get a list of top-level project dependencies"""
    project_deps = pyproject["project"]["dependencies"]
    additional_deps = get_dependency_group_deps(pyproject)
    top_level_deps: dict[str, str] = {}

    for dep in project_deps + additional_deps:
        match = re.search(PACKAGE_NAME_REGEX, dep, re.IGNORECASE)
        if not match:
            print(f"Failed to parse {dep}, invalid package name. Skipping...")
            continue
        version_specifiers = str(dep[match.end() :])  # Trim package name, keep as string to allow replacement
        top_level_deps[match[0]] = version_specifiers  # match[0] is package name

    return top_level_deps


def needs_sync(package_version: Version, specifiers: SpecifierSet) -> bool:
    return any(
        [
            spec
            for spec in specifiers
            if spec.operator in SUPPORTED_OPERATORS and Version(spec.version) != package_version
        ]
    )


def get_synced_version_specifier(package_version: Version, specifier: Specifier) -> Specifier:
    match specifier.operator:
        case VersionSpecifierOperators.COMPATIBLE:
            return specifier  # TODO: Implement
        case VersionSpecifierOperators.MATCHING:
            return specifier  # TODO: Implement
        case _:  # Greater than / greater than or equal
            return Specifier(f">={package_version}")


def get_synced_dependency(dependency: str, name: str, package_version: Version, specifiers: SpecifierSet) -> str:
    for specifier in specifiers:
        if specifier.operator in SUPPORTED_OPERATORS and Version(specifier.version) != package_version:
            synced_version_specifier = get_synced_version_specifier(package_version, specifier)
            print(f"Bumped {name} from {specifier.version} to {synced_version_specifier.version}")
            dependency = dependency.replace(str(specifier), str(synced_version_specifier))
    return dependency


def sync(workdir: Path) -> None:
    """Sync pyproject.toml dependency versions with versions in the uv.lock file"""
    pyproject = load_toml_file(workdir, "pyproject.toml")  # Load the pyproject.toml file
    lockfile = load_toml_file(workdir, "uv.lock")  # Load the uv.lock file as toml
    top_level_deps = get_dependencies(pyproject)  # Get direct project dependencies from all dependency groups
    top_level_packages = [  # Get top-level packages
        Package(name=pkg["name"], version=Version(pkg["version"]), specifiers=SpecifierSet(top_level_deps[pkg["name"]]))
        for pkg in lockfile["package"]
        if pkg["name"] in top_level_deps
    ]
    print(f"Found {len(top_level_packages)} top-level packages ({len(lockfile['package'])} total)")

    # Bump dependency specifier versions
    updated_deps: list[str] = []
    for package in top_level_packages:
        if needs_sync(package.version, package.specifiers):
            top_level_deps[package.name] = get_synced_dependency(
                top_level_deps[package.name], package.name, package.version, package.specifiers
            )
            updated_deps.append(package.name)

    print(f"Updated {len(updated_deps)} dependencies: {', '.join(updated_deps)}")


if __name__ == "__main__":
    sync(get_workdir())

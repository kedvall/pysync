# Pysync
Sync dependencies in your pyproject and uv lockfile!   

Note: This project is meant as a temporary solution until uv integrates this functional natively.   
See https://github.com/astral-sh/uv/issues/6794.

## Features
1. Pysync internally runs **uv sync** (passing through any relevant uv args) to ensure the lockfile is up to date
2. Pysync checks the minimum versions of top-level dependencies in your pyproject.toml file against installed versions
in your uv.lockfile
   - If they differ, pysync will bump the minimum version specified in the pyproject.toml file 
3. If any dependencies were updated, pysync will re-run the **uv sync** command to ensure the changes are valid and re-lock

## Installation
Install pysync via Homebrew:
```shell
brew tap kedvall/pysync
brew install pysync
```
Alternatively, grab the latest binary from the [releases page](https://github.com/kedvall/pysync/releases).   
Be sure to move it to a directory on your PATH and set execute permissions:
```shell
tar -xvzf pysync-macos.tar.gz
chmod +x pysync
sudo mv pysync /usr/local/bin/pysync
```

## Usage
Simply run the **pysync** command!   
```shell
pysync  # Syncs the environment of the current directory
```

The first argument (optional) sets the target directory, which defaults to the current directory:
```shell
pysync .  # Syncs the environment of the current directory
pysync ../another-project-dir  # Syncs the environment of another-project-dir
pysync sub-project  # Sync sub-project
pysync /absolute/path/to/my-project  # Syncs my-project
```
Any subsequent arguments are directly passed through to **uv sync**:
```shell
pysync --upgrade  # Runs 'uv sync --upgrade' then syncs the environment of the current directory
pysync --upgrade --index github=https://github.com/my-project  # Same, --index and other args are passed through
pysync test-project --upgrade  # Runs 'uv sync --upgrade' then syncs test-project
```
Pysync will automatically detect if the first arg given is a valid path.   
If not, and the given arg starts with -/--, pysync will automatically use the environment of the current directory:
```shell
# The following commands are equivalent: 
pysync
pysync .

# As are:
pysync --upgrade
pysync . --upgrade
```

## Known Issues
1. The [compatible release](https://packaging.python.org/en/latest/specifications/version-specifiers/#compatible-release) specifier is not yet supported
2. Dependencies written as a single-line list (i.e. of the form `dependencies = ["ruff>=0.10.0"]`) are currently not supported

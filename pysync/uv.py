import subprocess
import sys
from pathlib import Path

import typer
from rich import print


def uv_sync(workdir: Path, uv_passthrough_args: list[str] | None, silent: bool = False) -> None:
    stdout = None if silent else sys.stdout
    stderr = None if silent else sys.stderr
    command = ["uv", "sync"] + (uv_passthrough_args if uv_passthrough_args else [])
    if not silent:
        print(f"[bold cyan]Running {' '.join(command)}", flush=True)  # Print uv command that will be executed

    try:
        subprocess.run(command, cwd=workdir, check=True, stdout=stdout, stderr=stderr, capture_output=silent)
    except subprocess.CalledProcessError as e:
        error = f": {e}" if not silent else ""
        print(f"'{' '.join(e.cmd)}' failed with non-zero exit status {e.returncode} (workdir={workdir}){error}")
        raise typer.Exit(e.returncode) from None

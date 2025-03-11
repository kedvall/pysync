import subprocess
import sys
from pathlib import Path

import typer
from rich import print


def uv_sync(workdir: Path, uv_passthrough_args: list[str] | None) -> None:
    command = ["uv", "sync"] + (uv_passthrough_args if uv_passthrough_args else [])
    print(" ".join(command), flush=True)  # Print uv command that will be executed
    try:
        subprocess.run(command, cwd=workdir, check=True, stdout=sys.stdout, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"'{' '.join(e.cmd)}' failed with non-zero exit status {e.returncode} (workdir={workdir})")
        raise typer.Exit(e.returncode) from e
    print()  # Newline before additional pysync output

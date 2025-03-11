import subprocess
import sys
from pathlib import Path


def uv_sync(workdir: Path, *, upgrade: bool = False) -> None:
    args = ["uv", "sync"] + (["--upgrade"] if upgrade else [])  # Optionally upgrade packages
    print(" ".join(args), flush=True)  # Print uv command that will be executed
    try:
        subprocess.run(args, cwd=workdir, check=True, stdout=sys.stdout, stderr=sys.stderr)
    except subprocess.CalledProcessError as e:
        sys.exit(f"Failed to run uv sync: {e}")
    print()  # Newline before additional pysync output

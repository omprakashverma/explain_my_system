import shutil
import subprocess
import tempfile
from pathlib import Path

from fastapi import HTTPException

from backend.app.utils.file_utils import read_code_files_from_directory


def clone_repository(url: str) -> dict[str, str]:
    tmp = tempfile.mkdtemp(prefix="repo_")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", url, tmp],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "git clone failed"
            raise HTTPException(400, detail)
        return read_code_files_from_directory(Path(tmp))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

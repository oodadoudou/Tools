"""Resolve and inject the upstream Tooools backend path so we can import its modules."""
import sys
from pathlib import Path

UPSTREAM_BACKEND = Path("/Users/doudouda/Downloads/Personal_doc/Study/Proj/Tooools/file_process_tools/backend")

def ensure_on_path() -> None:
    p = str(UPSTREAM_BACKEND)
    if not UPSTREAM_BACKEND.is_dir():
        raise RuntimeError(
            f"Upstream backend not found at {UPSTREAM_BACKEND}. "
            "Adjust toolscli/upstream.py if the source moved."
        )
    if p not in sys.path:
        sys.path.insert(0, p)

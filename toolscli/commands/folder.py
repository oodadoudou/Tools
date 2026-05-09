"""Folder-level operations: flatten, organize-by-group, encode/decode-archive, ISO."""
import shutil
import subprocess
import sys
from pathlib import Path

from ..upstream import ensure_on_path
from ..result import print_result

ensure_on_path()
from modules.filename_manager import flatten_directories_api  # noqa: E402
from modules.file_organizer import organize_files_by_group_api  # noqa: E402
from modules.folder_processor import (  # noqa: E402
    encode_folders_with_double_compression_api,
    decode_folders_with_double_decompression_api,
)
from modules.iso_creator import process_subfolders_to_iso_api  # noqa: E402

ENCODE_SH = Path("/Users/doudouda/Downloads/Personal_doc/Study/shell_script/file_org/encode_folders.sh")
DECODE_SH = Path("/Users/doudouda/Downloads/Personal_doc/Study/shell_script/file_org/decode_folders.sh")


def flatten(args) -> int:
    return print_result(flatten_directories_api(args.dir))


def organize(args) -> int:
    if args.extensions:
        return print_result(organize_files_by_group_api(args.dir, args.extensions))
    return print_result(organize_files_by_group_api(args.dir))


def _run_shell(script: Path, cwd: str, label: str) -> int:
    """Drive the existing bash script in `cwd` (uses native 7z)."""
    if not script.is_file():
        print(f"[WARN] {script} missing, falling back to py7zr backend.", file=sys.stderr)
        return -1
    try:
        result = subprocess.run(
            ["bash", str(script)], cwd=cwd, check=False
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {label} shell failed: {exc}", file=sys.stderr)
        return 1
    return 0 if result.returncode == 0 else result.returncode


def encode_folder(args) -> int:
    if shutil.which("7z") and shutil.which("zip"):
        rc = _run_shell(ENCODE_SH, args.dir, "encode-folder")
        if rc >= 0:
            return rc
    print("[INFO] Using py7zr backend (native 7z unavailable).")
    return print_result(
        encode_folders_with_double_compression_api(args.dir, args.password)
    )


def decode_folder(args) -> int:
    if shutil.which("7z") and shutil.which("unzip"):
        rc = _run_shell(DECODE_SH, args.dir, "decode-folder")
        if rc >= 0:
            return rc
    print("[INFO] Using py7zr backend (native 7z unavailable).")
    return print_result(
        decode_folders_with_double_decompression_api(args.dir, args.password)
    )


def make_iso(args) -> int:
    parents = args.parents or [args.dir]
    return print_result(process_subfolders_to_iso_api(parents, args.output_dir))

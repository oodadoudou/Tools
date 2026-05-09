"""Filename batch operations."""
import sys
from pathlib import Path

from ..upstream import ensure_on_path
from ..result import print_result

ensure_on_path()
from modules.filename_manager import (  # noqa: E402
    add_filename_prefix_api,
    add_filename_suffix_api,
    delete_filename_chars_api,
    extract_numbers_in_filenames_api,
    rename_items_api,
    reverse_rename_api,
)


def extract_numbers(args) -> int:
    return print_result(extract_numbers_in_filenames_api(args.dir))


def delete_chars(args) -> int:
    return print_result(delete_filename_chars_api(args.dir, args.pattern))


def revert(args) -> int:
    return print_result(reverse_rename_api(args.dir))


def add_prefix(args) -> int:
    return print_result(add_filename_prefix_api(args.dir, args.prefix))


def add_suffix_native(args) -> int:
    """Backend-driven suffix add (works recursively per the upstream API)."""
    return print_result(add_filename_suffix_api(args.dir, args.suffix))


def _shallow_rename(args, *, kind: str) -> int:
    """Shell-script style top-level rename. kind ∈ {'suffix', 'prefix'}.
    Skips hidden items, preserves extensions for files, supports --dry-run.
    """
    fix = args.suffix if kind == "suffix" else args.prefix
    target_dir = Path(args.dir).resolve()
    if not target_dir.is_dir():
        print(f"[ERROR] '{target_dir}' is not a directory.", file=sys.stderr)
        return 2

    self_path = Path(sys.argv[0]).resolve()
    actions: list[tuple[Path, Path]] = []
    for item in sorted(target_dir.iterdir()):
        if item.resolve() == self_path:
            continue
        if not (item.is_file() or item.is_dir()):
            continue
        name = item.name
        if name.startswith("."):
            continue
        if kind == "suffix":
            if item.is_file() and "." in name:
                base, _, ext = name.rpartition(".")
                new_name = f"{base}{fix}.{ext}" if base else f"{name}{fix}"
            else:
                new_name = f"{name}{fix}"
        else:  # prefix
            new_name = f"{fix}{name}"
        if new_name == name:
            continue
        actions.append((item, item.with_name(new_name)))

    if args.dry_run:
        print(f"[DRY-RUN] Would rename {len(actions)} item(s):")
        for src, dst in actions:
            print(f"  '{src.name}' -> '{dst.name}'")
        return 0

    errors = 0
    for src, dst in actions:
        try:
            src.rename(dst)
            print(f"[SUCCESS] '{src.name}' -> '{dst.name}'")
        except Exception as exc:  # noqa: BLE001 — surface unexpected fs errors
            print(f"[ERROR] '{src.name}': {exc}", file=sys.stderr)
            errors += 1
    print(f"[INFO] Done. Renamed {len(actions) - errors}, errors {errors}.")
    return 0 if errors == 0 else 1


def add_suffix_shallow(args) -> int:
    """Shell-script style suffix add: top-level only, --dry-run, preserves extensions."""
    return _shallow_rename(args, kind="suffix")


def add_prefix_shallow(args) -> int:
    """Shell-script style prefix add: top-level only, --dry-run, hidden items skipped."""
    return _shallow_rename(args, kind="prefix")


def rename(args) -> int:
    mode = args.mode
    if mode not in ("files", "folders", "both"):
        print(f"[ERROR] Invalid rename mode: {mode!r}. Expect files|folders|both.", file=sys.stderr)
        return 2
    return print_result(rename_items_api(args.dir, mode))

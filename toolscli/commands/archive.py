"""Batch-compress per-folder archives (drives the upstream batch_compress_folders.py)."""
from __future__ import annotations

import sys
from pathlib import Path

UPSTREAM_DIR = Path("/Users/doudouda/Downloads/Personal_doc/Study/Proj/Scripts/archive_tools")
if str(UPSTREAM_DIR) not in sys.path:
    sys.path.insert(0, str(UPSTREAM_DIR))

import batch_compress_folders as bcf  # noqa: E402


def batch_compress(args) -> int:
    """Non-interactive variant of bcf.main(): batch-compress each subfolder of --root.

    For every comic folder in --root:
      1. Move it under --finished
      2. Find its `*_pdf` / `*_pdfs` subfolder
      3. Compress that subfolder into <root>/PDF/<comic>.7z (split when >1.8GB)
    """
    root_path = Path(args.root).expanduser().resolve()
    if not root_path.is_dir():
        print(f"[ERROR] root '{root_path}' is not a directory.", file=sys.stderr)
        return 1

    finished = args.finished or f"{root_path}_Finished"
    finished_root = Path(finished).expanduser().resolve()
    try:
        finished_root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"[ERROR] cannot create finished dir '{finished_root}': {exc}", file=sys.stderr)
        return 1

    try:
        backend = bcf.get_backend()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    exclude = {bcf.PDF_FOLDER_NAME}
    if finished_root.parent == root_path:
        exclude.add(finished_root.name)

    comic_folders = bcf.list_target_folders(root_path, exclude_names=exclude)
    if not comic_folders:
        print(f"[INFO] No comic folders to process under '{root_path}'.")
        return 0

    pdf_root = root_path / bcf.PDF_FOLDER_NAME
    pdf_root.mkdir(exist_ok=True)

    print(f"[INFO] Root        : {root_path}")
    print(f"[INFO] Finished    : {finished_root}")
    print(f"[INFO] Output dir  : {pdf_root}")
    print(f"[INFO] Backend     : {backend[0]}")
    print(f"[INFO] Targets     : {len(comic_folders)}")
    print("-" * 60)

    success = skipped = 0
    failed: list[bcf.CompressionResult] = []

    for index, comic in enumerate(comic_folders, start=1):
        try:
            finished_dir, archive_base = bcf.move_comic_to_finished(finished_root, comic)
        except Exception as exc:  # noqa: BLE001 — surface unexpected fs errors
            print(f"[{index}/{len(comic_folders)}] [FAIL] {comic.name} -> move failed: {exc}")
            failed.append(bcf.CompressionResult(comic.name, "failed", f"move failed: {exc}"))
            continue

        pdf_sub = bcf.find_pdf_subfolder(finished_dir)
        if pdf_sub is None:
            print(f"[{index}/{len(comic_folders)}] [SKIP] {archive_base} -> no *_pdf/*_pdfs subfolder")
            skipped += 1
            continue

        result = bcf.compress_comic_pdf(pdf_root, finished_dir, pdf_sub, archive_base, backend)
        tag = {"success": "OK", "skipped": "SKIP", "failed": "FAIL"}.get(result.status, result.status.upper())
        print(f"[{index}/{len(comic_folders)}] [{tag}] {result.folder_name} -> {result.message}")
        if result.status == "success":
            success += 1
        elif result.status == "skipped":
            skipped += 1
        else:
            failed.append(result)

    print("-" * 60)
    print(f"[INFO] success={success} skipped={skipped} failed={len(failed)}")
    if failed:
        print("[INFO] Failures:")
        for item in failed:
            print(f"  - {item.folder_name}: {item.message}")
    return 0 if not failed else 2

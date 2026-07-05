#!/usr/bin/env python3
"""Tooools CLI — single entry exposing all file_process_tools backend ops.

Two interchangeable invocation styles:

  Subcommands (preferred for new use):
    tools name extract-numbers
    tools pdf encode --password 1111
    tools folder organize
    tools combine pdf --name merged

  Legacy short flags (kept for the existing zsh aliases tn/tf/tcp/...):
    tools -N            tools -F            tools -C p
    tools -D "删"       tools -V            tools -B _bak
    tools --encode-pdf 1111   tools --decode-pdf [pwd]
    tools -R folders    tools -FO

Run `tools -h` for the full subcommand tree, or `tools <group> -h` per group.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys

from toolscli.commands import name as cmd_name
from toolscli.commands import folder as cmd_folder
from toolscli.commands import combine as cmd_combine
from toolscli.commands import pdf as cmd_pdf
from toolscli.commands import image as cmd_image
from toolscli.commands import archive as cmd_archive


# ---------- subcommand registration ----------

def _add_dir(p: argparse.ArgumentParser) -> None:
    p.add_argument("-d", "--dir", default=os.getcwd(),
                   help="Target directory (default: cwd).")


def _add_outdir(p: argparse.ArgumentParser) -> None:
    p.add_argument("-o", "--output-dir", default=None,
                   help="Output directory (default: same as --dir).")


def _build_name(sub: argparse._SubParsersAction) -> None:
    g = sub.add_parser("name", help="Filename batch operations.").add_subparsers(
        dest="action", required=True
    )

    p = g.add_parser("extract-numbers", help="Keep only the numeric sequence in each filename.")
    _add_dir(p); p.set_defaults(func=cmd_name.extract_numbers)

    p = g.add_parser("delete", help="Delete a regex pattern from filenames.")
    _add_dir(p); p.add_argument("pattern"); p.set_defaults(func=cmd_name.delete_chars)

    p = g.add_parser("revert", help="Revert the last rename op (uses upstream's rename log).")
    _add_dir(p); p.set_defaults(func=cmd_name.revert)

    p = g.add_parser("prefix", help="Add a prefix (top-level only, supports --dry-run).")
    _add_dir(p); p.add_argument("prefix"); p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_name.add_prefix_shallow)

    p = g.add_parser("prefix-deep", help="Add a prefix using upstream backend.")
    _add_dir(p); p.add_argument("prefix"); p.set_defaults(func=cmd_name.add_prefix)

    p = g.add_parser("suffix", help="Add a suffix (top-level only, supports --dry-run).")
    _add_dir(p); p.add_argument("suffix"); p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_name.add_suffix_shallow)

    p = g.add_parser("suffix-deep", help="Add a suffix using upstream backend (recursive logic).")
    _add_dir(p); p.add_argument("suffix"); p.set_defaults(func=cmd_name.add_suffix_native)

    p = g.add_parser("rename", help="Batch rename items by pattern (files / folders / both).")
    _add_dir(p); p.add_argument("mode", choices=["files", "folders", "both"])
    p.set_defaults(func=cmd_name.rename)


def _build_folder(sub: argparse._SubParsersAction) -> None:
    g = sub.add_parser("folder", help="Folder ops: flatten / organize / encode / iso.").add_subparsers(
        dest="action", required=True
    )

    p = g.add_parser("flatten", help="Move all files in subdirectories up to the root.")
    _add_dir(p); p.set_defaults(func=cmd_folder.flatten)

    p = g.add_parser("organize", help="Group files by common name prefix into subfolders.")
    _add_dir(p)
    p.add_argument("--extensions", default=None,
                   help='Space-separated extensions (e.g. ".pdf .epub"). Defaults to upstream set.')
    p.set_defaults(func=cmd_folder.organize)

    p = g.add_parser("encode", help="Encrypt+double-compress each top-level subfolder (.z删ip output).")
    _add_dir(p); p.add_argument("--password", default="1111")
    p.set_defaults(func=cmd_folder.encode_folder)

    p = g.add_parser("decode", help="Reverse `folder encode` on .z删ip files in DIR.")
    _add_dir(p); p.add_argument("--password", default="1111")
    p.set_defaults(func=cmd_folder.decode_folder)

    p = g.add_parser("iso", help="Create one ISO per subfolder of DIR.")
    _add_dir(p); _add_outdir(p)
    p.add_argument("--parents", nargs="*", default=None,
                   help="Override: explicit list of parent dirs (default: just --dir).")
    p.set_defaults(func=cmd_folder.make_iso)


def _build_combine(sub: argparse._SubParsersAction) -> None:
    g = sub.add_parser("combine", help="Merge / convert files (pdf / txt / epub).").add_subparsers(
        dest="action", required=True
    )

    def _common(p: argparse.ArgumentParser) -> None:
        _add_dir(p); _add_outdir(p)
        p.add_argument("--name", default="merged", help="Output base name (default: merged).")

    p = g.add_parser("pdf", help="Concatenate all PDFs in DIR.")
    _common(p); p.set_defaults(func=cmd_combine.combine, type="p")

    p = g.add_parser("txt", help="Concatenate all TXTs in DIR.")
    _common(p); p.set_defaults(func=cmd_combine.combine, type="t")

    p = g.add_parser("epub", help="Convert each EPUB in DIR to TXT.")
    _add_dir(p); _add_outdir(p)
    p.set_defaults(func=cmd_combine.combine, type="e", name="merged")


def _build_pdf(sub: argparse._SubParsersAction) -> None:
    g = sub.add_parser("pdf", help="PDF: encrypt / decrypt / trim / repair / convert.").add_subparsers(
        dest="action", required=True
    )

    p = g.add_parser("encode", help="Password-encrypt all PDFs in DIR.")
    _add_dir(p); _add_outdir(p); p.add_argument("--password", required=True)
    p.set_defaults(func=cmd_pdf.encode)

    p = g.add_parser("decode", help="Decrypt PDFs in DIR (in place).")
    _add_dir(p); p.add_argument("--password", default="")
    p.set_defaults(func=cmd_pdf.decode)

    p = g.add_parser("trim", help="Remove pages from each PDF.")
    _add_dir(p); _add_outdir(p)
    p.add_argument("--where", choices=["f", "l", "b"], default="f",
                   help="f=first, l=last, b=both ends.")
    p.add_argument("--num-pages", type=int, default=1)
    p.add_argument("--pages", default=None,
                   help="Specific pages to remove (e.g. '1,3,5-7'). Overrides --where.")
    p.set_defaults(func=cmd_pdf.trim)

    p = g.add_parser("repair", help="Rebuild PDFs to repair corruption.")
    _add_dir(p); _add_outdir(p); p.set_defaults(func=cmd_pdf.repair)

    p = g.add_parser("to-txt", help="Extract text from each PDF as .txt.")
    _add_dir(p); _add_outdir(p)
    p.add_argument("--format", default="standard")
    p.set_defaults(func=cmd_pdf.to_txt)

    p = g.add_parser("to-image", help="Render each PDF page as an image.")
    _add_dir(p); _add_outdir(p)
    p.add_argument("--format", default="png", choices=["png", "jpg"])
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--quality", type=int, default=90)
    p.set_defaults(func=cmd_pdf.to_image)


def _build_archive(sub: argparse._SubParsersAction) -> None:
    g = sub.add_parser("archive", help="Batch archive ops.").add_subparsers(
        dest="action", required=True
    )

    p = g.add_parser(
        "compress",
        help="For each subfolder of --root, move it to --finished, find its *_pdf "
             "subfolder and compress to <root>/PDF/<name>.7z (auto-splits >1.8GB).",
    )
    p.add_argument("--root", default=os.getcwd(),
                   help="Root containing one comic folder per subdir (default: cwd).")
    p.add_argument("--finished", default=None,
                   help="Where finished comic folders are moved (default: <root>_Finished).")
    p.set_defaults(func=cmd_archive.batch_compress)


def _build_image(sub: argparse._SubParsersAction) -> None:
    g = sub.add_parser("image", help="Image ops: images→PDF, compress.").add_subparsers(
        dest="action", required=True
    )

    def _common(p: argparse.ArgumentParser) -> None:
        _add_dir(p); _add_outdir(p)
        p.add_argument("--name", default="combined_images")
        p.add_argument("--target-width", type=int, default=1500)
        p.add_argument("--dpi", type=int, default=300)

    p = g.add_parser("to-pdf", help="Combine images in DIR into a single PDF.")
    _common(p); p.set_defaults(func=cmd_image.to_pdf)

    p = g.add_parser("compress", help="Compress images and emit a PDF.")
    _common(p); p.add_argument_group()
    p.set_defaults(func=cmd_image.compress, name="compressed_images")


# ---------- legacy short-flag dispatcher ----------

def _legacy_parser() -> argparse.ArgumentParser:
    """Mirrors the original `tools -X` flag style used by the user's zsh aliases."""
    p = argparse.ArgumentParser(prog="tools", add_help=False)
    p.add_argument("-d", "--dir", default=os.getcwd())
    p.add_argument("-o", "--output-dir", default=None)
    p.add_argument("--name", default="merged")
    p.add_argument("--dry-run", action="store_true")

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-N", "--extract-numbers", action="store_true")
    g.add_argument("-F", "--flatten", action="store_true")
    g.add_argument("-C", "--combine", choices=["p", "t", "e"], metavar="TYPE")
    g.add_argument("-D", "--delete-chars", metavar="PATTERN")
    g.add_argument("-V", "--revert", action="store_true")
    g.add_argument("-B", "--add-suffix", metavar="SUFFIX")
    g.add_argument("-P", "--add-prefix-shallow", metavar="PREFIX")
    g.add_argument("-A", "--add-prefix", metavar="PREFIX")
    g.add_argument("-R", "--rename", choices=["files", "folders", "both"], metavar="MODE")
    g.add_argument("-FO", "--organize", action="store_true",
                   help="Group files by common name prefix into subfolders.")
    g.add_argument("-Z", "--zfile", action="store_true",
                   help="Batch-compress comic folders (see `tools archive compress`).")
    g.add_argument("--encode-pdf", metavar="PASSWORD")
    g.add_argument("--decode-pdf", nargs="?", const="", metavar="PASSWORD")
    g.add_argument("--encode-folder", action="store_true")
    g.add_argument("--decode-folder", action="store_true")
    p.add_argument("--password", default="1111", help="Password for encode-folder/decode-folder.")
    p.add_argument("--root", default=None, help="Root for -Z (default: --dir).")
    p.add_argument("--finished", default=None, help="Finished dir for -Z (default: <root>_Finished).")
    # Optional trailing positional: merged output base name for -C p / -C t
    # (e.g. `tcp 棋子的世界-台`). Falls back to --name / "merged" when omitted.
    p.add_argument("name_pos", nargs="?", default=None, help=argparse.SUPPRESS)
    return p


def _looks_like_legacy(argv: list[str]) -> bool:
    """A token starts with - and isn't '-h/--help' → treat as legacy short-flag mode."""
    short = {"-N", "-F", "-C", "-D", "-V", "-B", "-P", "-A", "-R", "-FO", "-Z"}
    long_ = {"--encode-pdf", "--decode-pdf", "--encode-folder", "--decode-folder"}
    return any(a in short or a in long_ for a in argv)


def _dispatch_legacy(argv: list[str]) -> int:
    args = _legacy_parser().parse_args(argv)
    if args.output_dir is None:
        args.output_dir = args.dir

    if args.extract_numbers:
        return cmd_name.extract_numbers(args)
    if args.flatten:
        return cmd_folder.flatten(args)
    if args.combine:
        args.type = args.combine
        if args.name_pos:
            args.name = args.name_pos
        return cmd_combine.combine(args)
    if args.delete_chars is not None:
        args.pattern = args.delete_chars
        return cmd_name.delete_chars(args)
    if args.revert:
        return cmd_name.revert(args)
    if args.add_suffix is not None:
        args.suffix = args.add_suffix
        return cmd_name.add_suffix_shallow(args)
    if args.add_prefix_shallow is not None:
        args.prefix = args.add_prefix_shallow
        return cmd_name.add_prefix_shallow(args)
    if args.add_prefix is not None:
        args.prefix = args.add_prefix
        return cmd_name.add_prefix(args)
    if args.rename is not None:
        args.mode = args.rename
        return cmd_name.rename(args)
    if args.organize:
        args.extensions = None
        return cmd_folder.organize(args)
    if args.zfile:
        if args.root is None:
            args.root = args.dir
        return cmd_archive.batch_compress(args)
    if args.encode_pdf is not None:
        args.password = args.encode_pdf
        return cmd_pdf.encode(args)
    if args.decode_pdf is not None:
        args.password = args.decode_pdf
        return cmd_pdf.decode(args)
    if args.encode_folder:
        return cmd_folder.encode_folder(args)
    if args.decode_folder:
        return cmd_folder.decode_folder(args)
    return 2


# ---------- main ----------

def _build_root() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tools",
        description="Tooools file-processing CLI. Use `tools <group> -h` for details.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Legacy short-flag form (also supported):\n"
            "  tools -N | -F | -C {p,t,e} | -D PATTERN | -V | -B SUFFIX |\n"
            "        -A PREFIX | -R {files,folders,both} | -FO | -Z |\n"
            "        --encode-pdf PWD | --decode-pdf [PWD] |\n"
            "        --encode-folder [--password PWD] | --decode-folder"
        ),
    )
    sub = p.add_subparsers(dest="group")
    _build_name(sub)
    _build_folder(sub)
    _build_combine(sub)
    _build_pdf(sub)
    _build_image(sub)
    _build_archive(sub)
    return p


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.WARNING, format="%(message)s")
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv:
        _build_root().print_help()
        return 0

    if _looks_like_legacy(argv):
        return _dispatch_legacy(argv)

    parser = _build_root()
    args = parser.parse_args(argv)
    if not getattr(args, "group", None):
        parser.print_help()
        return 0
    if getattr(args, "output_dir", None) is None:
        args.output_dir = getattr(args, "dir", os.getcwd())
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

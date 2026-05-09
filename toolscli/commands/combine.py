"""Combine/merge files."""
import sys

from ..upstream import ensure_on_path
from ..result import print_result

ensure_on_path()
from modules.file_combiner import combine_files_api  # noqa: E402
from modules.text_converter import epub_to_txt_api  # noqa: E402


def combine(args) -> int:
    type_char = args.type
    if type_char == "e":
        return print_result(epub_to_txt_api(args.dir, args.output_dir))
    if type_char in ("p", "t"):
        return print_result(
            combine_files_api(args.dir, args.output_dir, type_char, args.name)
        )
    print(f"[ERROR] Unsupported combine type: {type_char!r} (expect p|t|e).", file=sys.stderr)
    return 2

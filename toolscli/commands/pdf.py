"""PDF operations: encrypt, decrypt, trim pages, repair, to-txt, to-image."""
import sys

from ..upstream import ensure_on_path
from ..result import print_result

ensure_on_path()
from modules.pdf_security_processor import encode_pdfs_api, decode_pdfs_api  # noqa: E402
from modules.pdf_processor import (  # noqa: E402
    remove_pdf_pages_api,
    process_pdfs_for_specific_page_removal_api,
    repair_pdfs_by_rebuilding_api,
)
from modules.text_converter import pdf_to_txt_api  # noqa: E402
from modules.image_converter import pdf_to_images_api  # noqa: E402


def encode(args) -> int:
    return print_result(encode_pdfs_api(args.dir, args.output_dir, args.password))


def decode(args) -> int:
    return print_result(decode_pdfs_api(args.dir, args.password or ""))


def trim(args) -> int:
    if args.pages:
        return print_result(
            process_pdfs_for_specific_page_removal_api(args.dir, args.output_dir, args.pages)
        )
    trim_type = args.where  # 'f' first, 'l' last, 'b' both
    if trim_type not in ("f", "l", "b"):
        print(f"[ERROR] --where must be f|l|b (got {trim_type!r}).", file=sys.stderr)
        return 2
    return print_result(
        remove_pdf_pages_api(args.dir, args.output_dir, trim_type, args.num_pages)
    )


def repair(args) -> int:
    return print_result(repair_pdfs_by_rebuilding_api(args.dir, args.output_dir))


def to_txt(args) -> int:
    return print_result(pdf_to_txt_api(args.dir, args.output_dir, args.format))


def to_image(args) -> int:
    return print_result(
        pdf_to_images_api(args.dir, args.output_dir, args.format, args.dpi, args.quality)
    )

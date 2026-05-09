"""Image operations: images→PDF, image compression."""
from ..upstream import ensure_on_path
from ..result import print_result

ensure_on_path()
from modules.image_converter import images_to_pdf_api, compress_images_api  # noqa: E402


def to_pdf(args) -> int:
    return print_result(
        images_to_pdf_api(args.dir, args.output_dir, args.name, args.target_width, args.dpi)
    )


def compress(args) -> int:
    return print_result(
        compress_images_api(args.dir, args.output_dir, args.name, args.target_width, args.dpi)
    )

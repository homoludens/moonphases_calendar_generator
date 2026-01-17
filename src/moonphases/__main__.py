"""Command-line interface for moonphases."""

import argparse
from datetime import datetime
from pathlib import Path

from .calendar import build_svg, DEFAULT_FONT_PATH
from .downloader import download_moon_images
from .themes import DEFAULT_THEME, list_themes


def get_default_year() -> int:
    """Return current year, or next year if we're in December."""
    now = datetime.now()
    if now.month == 12:
        return now.year + 1
    return now.year


def main():
    parser = argparse.ArgumentParser(description="Generate moon phase calendar SVG")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download command
    dl_parser = subparsers.add_parser("download", help="Download moon phase images")
    dl_parser.add_argument(
        "-o", "--output", type=Path, default=Path("images"),
        help="Output directory for images (default: images)"
    )
    dl_parser.add_argument(
        "-n", "--count", type=int, default=15,
        help="Number of images to download (default: 15)"
    )

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate calendar SVG")
    gen_parser.add_argument(
        "year", type=int, nargs="?", default=None,
        help="Year for the calendar (default: current year, or next year in December)"
    )
    gen_parser.add_argument(
        "-i", "--images", type=Path, default=Path("moonphases"),
        help="Directory containing moon phase images (default: moonphases)"
    )
    gen_parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output SVG file (default: moon_calendar_YEAR.svg)"
    )
    gen_parser.add_argument(
        "--img-size", type=int, default=30,
        help="Size of moon images in SVG (default: 30)"
    )
    gen_parser.add_argument(
        "-t", "--theme", type=str, default="yellow",
        help=f"Theme name (available: {', '.join(list_themes())}; default: yellow)"
    )
    gen_parser.add_argument(
        "--lat", "--latitude", type=float, default=None, dest="latitude",
        help="Observer latitude in degrees for moon tilt (e.g., 45.0 for 45°N, -33.9 for Sydney)"
    )
    gen_parser.add_argument(
        "--font", type=Path, default=Path("moonphases/fonts/immortal.ttf"),
        help="Path to TTF/OTF font file to embed (default: moonphases/fonts/immortal.ttf)"
    )
    gen_parser.add_argument(
        "--font-family", type=str, default=None,
        help="Font family name for CSS (default: derived from font filename)"
    )
    gen_parser.add_argument(
        "--embed-images", action="store_true", default=True,
        help="Embed images as base64 data URIs in the SVG (default: True)"
    )
    gen_parser.add_argument(
        "--no-embed-images", action="store_false", dest="embed_images",
        help="Don't embed images, use file references instead"
    )
    gen_parser.add_argument(
        "--create-pdf", action="store_true", default=True,
        help="Also create a PDF version of the calendar (default: True, requires playwright)"
    )
    gen_parser.add_argument(
        "--no-pdf", action="store_false", dest="create_pdf",
        help="Don't create PDF, only generate SVG"
    )
    gen_parser.add_argument(
        "--pdf-format", type=str, default="A3",
        help="PDF page format (default: A3). Options: A3, A4, Letter, etc."
    )

    args = parser.parse_args()

    if args.command == "download":
        paths = download_moon_images(args.output, args.count)
        print(f"Downloaded {len(paths)} images to {args.output}")

    elif args.command == "generate":
        year = args.year if args.year is not None else get_default_year()
        output = args.output or Path(f"moon_calendar_{year}.svg")
        build_svg(
            year=year,
            image_dir=args.images,
            out_svg=output,
            img_size=args.img_size,
            link_base=str(args.images),
            theme=args.theme,
            latitude=args.latitude,
            font_path=args.font,
            font_family=args.font_family,
            embed_images=args.embed_images,
        )
        print(f"Generated: {output.resolve()}")

        if args.create_pdf:
            try:
                from .svg_to_pdf import svg_to_pdf
            except ImportError:
                print("Error: --create-pdf requires playwright. Install it with: pip install playwright && playwright install chromium")
                raise SystemExit(1)

            pdf_output = output.with_suffix(".pdf")
            svg_to_pdf(
                svg_path=output,
                pdf_path=pdf_output,
                page_format=args.pdf_format,
            )
            print(f"Generated: {pdf_output.resolve()}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

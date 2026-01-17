"""Command-line interface for moonphases."""

import argparse
from pathlib import Path

from .calendar import build_svg
from .downloader import download_moon_images


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
    gen_parser.add_argument("year", type=int, help="Year for the calendar")
    gen_parser.add_argument(
        "-i", "--images", type=Path, default=Path("images"),
        help="Directory containing moon phase images (default: images)"
    )
    gen_parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Output SVG file (default: moon_calendar_YEAR.svg)"
    )
    gen_parser.add_argument(
        "--img-size", type=int, default=30,
        help="Size of moon images in SVG (default: 30)"
    )

    args = parser.parse_args()

    if args.command == "download":
        paths = download_moon_images(args.output, args.count)
        print(f"Downloaded {len(paths)} images to {args.output}")

    elif args.command == "generate":
        output = args.output or Path(f"moon_calendar_{args.year}.svg")
        build_svg(
            year=args.year,
            image_dir=args.images,
            out_svg=output,
            img_size=args.img_size,
            link_base=str(args.images),
        )
        print(f"Generated: {output.resolve()}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

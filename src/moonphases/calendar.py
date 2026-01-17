"""Moon phase calendar SVG generator."""

from __future__ import annotations

import calendar
import datetime as dt
import os
from pathlib import Path
from urllib.parse import quote

SYNODIC_MONTH = 29.53058867  # days

# Reference new moon (approx): 2000-01-06 18:14 UTC
REF_NEW_MOON_UTC = dt.datetime(2000, 1, 6, 18, 14, tzinfo=dt.timezone.utc)


def moon_phase_fraction(date_utc: dt.datetime) -> float:
    """
    Returns phase in [0,1):
      0.0 ~ new moon
      0.5 ~ full moon
    """
    delta_days = (date_utc - REF_NEW_MOON_UTC).total_seconds() / 86400.0
    return (delta_days % SYNODIC_MONTH) / SYNODIC_MONTH


def choose_icon_index(phase_frac: float, max_index: int) -> int:
    """
    Map phase fraction to discrete icon index 0..max_index.
    If max_index is 28, that gives ~daily steps through a lunation.
    If max_index is 14, it gives waxing-only steps 0..full.
    """
    idx = int(round(phase_frac * max_index)) % (max_index + 1)
    return idx


def file_exists(image_dir: Path, idx: int, prefix: str = "d_150_", ext: str = ".jpg") -> bool:
    return (image_dir / f"{prefix}{idx}{ext}").exists()


def build_svg(
    year: int,
    image_dir: Path,
    out_svg: Path,
    img_size: int = 30,
    gap_x: int = 18,
    gap_y: int = 6,
    margin_left: int = 56,
    margin_top: int = 70,
    bg_color: str = "#000000",
    fg_color: str = "#ffffff",
    prefix: str = "d_150_",
    ext: str = ".jpg",
    link_base: str | None = None,
) -> None:
    """
    Create an SVG calendar:
      columns = months (Jan..Dec)
      rows    = days (1..31)

    `link_base` controls href paths in SVG:
      - None => use filenames only (e.g. d_150_3.jpg)
      - "images" => images/d_150_3.jpg
      - absolute path also possible (not always portable)
    """

    # Decide if you have a full lunation set (0..28) or only 0..14
    has_28 = all(file_exists(image_dir, i, prefix, ext) for i in range(0, 29))
    has_14 = all(file_exists(image_dir, i, prefix, ext) for i in range(0, 15))

    if not (has_28 or has_14):
        raise FileNotFoundError(
            f"Could not find a complete icon set in {image_dir}.\n"
            f"Expected either {prefix}0..{prefix}28{ext} OR {prefix}0..{prefix}14{ext}."
        )

    max_index = 28 if has_28 else 14

    months = list("JFMAMJJASOND")

    # Geometry
    col_w = img_size + gap_x
    row_h = img_size + gap_y

    # Extra room for month letters and side day numbers
    width = margin_left + 12 * col_w + margin_left
    height = margin_top + 31 * row_h + 40

    def href_for(idx: int) -> str:
        fname = f"{prefix}{idx}{ext}"
        if link_base:
            return quote(str(Path(link_base) / fname).replace(os.sep, "/"))
        return quote(fname)

    # Start SVG
    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{bg_color}"/>')

    # Title
    parts.append(
        f'<text x="{width/2:.1f}" y="42" text-anchor="middle" '
        f'font-family="serif" font-size="32" fill="{fg_color}">{year}</text>'
    )

    # Month letters
    for m, letter in enumerate(months, start=1):
        x = margin_left + (m - 1) * col_w + img_size / 2
        parts.append(
            f'<text x="{x:.1f}" y="{margin_top-18}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="16" fill="{fg_color}">{letter}</text>'
        )

    # Day numbers left & right
    for day in range(1, 32):
        y = margin_top + (day - 1) * row_h + img_size * 0.75
        parts.append(
            f'<text x="{margin_left-18}" y="{y:.1f}" text-anchor="end" '
            f'font-family="sans-serif" font-size="16" fill="{fg_color}">{day}</text>'
        )
        parts.append(
            f'<text x="{width-(margin_left-18)}" y="{y:.1f}" text-anchor="start" '
            f'font-family="sans-serif" font-size="16" fill="{fg_color}">{day}</text>'
        )

    # Images grid
    for month in range(1, 13):
        _, days_in_month = calendar.monthrange(year, month)
        for day in range(1, 32):
            if day > days_in_month:
                continue

            # Use noon UTC to reduce timezone edge effects
            d = dt.datetime(year, month, day, 12, 0, tzinfo=dt.timezone.utc)
            frac = moon_phase_fraction(d)

            if max_index == 28:
                idx = choose_icon_index(frac, 28)
                flip = False
                use_idx = idx
            else:
                # Only 0..14 available (waxing). Mirror for waning.
                pos = choose_icon_index(frac, 28)
                if pos <= 14:
                    use_idx = pos
                    flip = False
                else:
                    use_idx = 28 - pos
                    flip = True

            x = margin_left + (month - 1) * col_w
            y = margin_top + (day - 1) * row_h

            href = href_for(use_idx)

            if not flip:
                parts.append(
                    f'<image href="{href}" x="{x}" y="{y}" '
                    f'width="{img_size}" height="{img_size}" />'
                )
            else:
                cx = x + img_size / 2
                cy = y + img_size / 2
                parts.append(
                    f'<g transform="translate({cx},{cy}) scale(-1,1) translate({-cx},{-cy})">'
                    f'<image href="{href}" x="{x}" y="{y}" '
                    f'width="{img_size}" height="{img_size}" />'
                    f'</g>'
                )

    parts.append("</svg>")

    out_svg.write_text("\n".join(parts), encoding="utf-8")

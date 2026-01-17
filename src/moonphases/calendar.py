"""Moon phase calendar SVG generator."""

from __future__ import annotations

import base64
import calendar
import datetime as dt
import math
import os
from pathlib import Path
from urllib.parse import quote

from .themes import DEFAULT_THEME, Theme, get_theme, resolve_theme_dir

# Default font path (relative to package)
DEFAULT_FONT_PATH = Path(__file__).parent.parent.parent / "moonphases" / "fonts" / "URWBookman-Demi.ttf"
DEFAULT_FONT_FAMILY = "URWBookman-Demi"

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


def moon_tilt_angle(date_utc: dt.datetime, latitude: float) -> float:
    """
    Calculate the approximate moon tilt angle (parallactic angle) for display.

    The moon's apparent tilt depends on the observer's latitude and the moon's
    position in the sky. This is a simplified calculation that gives a visually
    reasonable approximation.

    Args:
        date_utc: Date/time in UTC
        latitude: Observer's latitude in degrees (positive = North)

    Returns:
        Tilt angle in degrees. Positive = clockwise rotation.
    """
    # Get day of year for seasonal variation
    day_of_year = date_utc.timetuple().tm_yday

    # Moon's declination varies roughly between -28.5 and +28.5 degrees
    # over an 18.6-year cycle, simplified here to annual variation
    # Plus monthly variation due to moon's orbit
    days_since_ref = (date_utc - REF_NEW_MOON_UTC).total_seconds() / 86400.0

    # Approximate moon declination (simplified)
    # Annual component (sun's position affects moon's path)
    annual_angle = 2 * math.pi * day_of_year / 365.25
    # Monthly component (moon's orbital inclination ~5 degrees)
    monthly_angle = 2 * math.pi * (days_since_ref % 27.32) / 27.32

    moon_dec = 23.4 * math.sin(annual_angle) + 5.1 * math.sin(monthly_angle)
    moon_dec_rad = math.radians(moon_dec)

    # Observer latitude
    lat_rad = math.radians(latitude)

    # Simplified parallactic angle calculation
    # When moon is on meridian (hour angle = 0), parallactic angle depends on
    # the difference between observer latitude and moon declination
    # This gives the "tilt" of the terminator line

    # The tilt angle is approximately:
    # tilt = latitude - moon_declination (when moon is on meridian)
    # This is simplified but gives visually correct results for most purposes
    tilt = latitude - moon_dec

    return tilt


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
    bg_color: str | None = None,
    fg_color: str | None = None,
    link_base: str | None = None,
    theme: str | Theme = DEFAULT_THEME,
    latitude: float | None = None,
    font_path: Path | None = None,
    font_family: str | None = None,
) -> None:
    """
    Create an SVG calendar:
      columns = months (Jan..Dec)
      rows    = days (1..31)

    Args:
        year: Calendar year
        image_dir: Base directory containing moon images (or theme subdirectories)
        out_svg: Output SVG file path
        img_size: Size of moon images in pixels
        gap_x: Horizontal gap between images
        gap_y: Vertical gap between images
        margin_left: Left margin
        margin_top: Top margin
        bg_color: Background color (overrides theme)
        fg_color: Foreground/text color (overrides theme)
        link_base: Base path for SVG hrefs (None = filenames only)
        theme: Theme name or Theme object
        latitude: Observer latitude in degrees for moon tilt (None = no rotation)
        font_path: Path to TTF/OTF font file to embed (None = use default)
        font_family: Font family name for CSS (None = derive from font filename)
    """
    # Resolve theme
    if isinstance(theme, str):
        theme_obj = get_theme(theme)
    else:
        theme_obj = theme

    # Use theme defaults, allow overrides
    bg_color = bg_color if bg_color is not None else theme_obj.bg_color
    fg_color = fg_color if fg_color is not None else theme_obj.fg_color

    # Resolve font
    if font_path is None:
        font_path = DEFAULT_FONT_PATH
    if font_family is None:
        font_family = font_path.stem if font_path.exists() else DEFAULT_FONT_FAMILY

    # Load and encode font if it exists
    font_style = ""
    if font_path.exists():
        font_data = font_path.read_bytes()
        font_b64 = base64.b64encode(font_data).decode("ascii")
        font_ext = font_path.suffix.lower()
        font_format = "truetype" if font_ext == ".ttf" else "opentype"
        font_style = f"""<style>
@font-face {{
  font-family: '{font_family}';
  src: url('data:font/{font_ext[1:]};base64,{font_b64}') format('{font_format}');
}}
</style>"""

    # Resolve image directory (check for theme subdirectory)
    original_image_dir = image_dir
    image_dir = resolve_theme_dir(image_dir, theme_obj.name)

    # Update link_base if theme subdirectory was used
    if link_base and image_dir != original_image_dir:
        link_base = str(Path(link_base) / f"theme_{theme_obj.name}")

    # Verify images exist
    missing = []
    for i in range(0, theme_obj.max_index + 1):
        if not theme_obj.image_path(image_dir, i, waning=False).exists():
            missing.append(theme_obj.image_filename(i, waning=False))
    if missing:
        raise FileNotFoundError(
            f"Missing images in {image_dir}: {missing[:5]}{'...' if len(missing) > 5 else ''}"
        )

    if theme_obj.has_waning_images:
        missing = []
        for i in range(0, theme_obj.max_index + 1):
            if not theme_obj.image_path(image_dir, i, waning=True).exists():
                missing.append(theme_obj.image_filename(i, waning=True))
        if missing:
            raise FileNotFoundError(
                f"Missing waning images in {image_dir}: {missing[:5]}{'...' if len(missing) > 5 else ''}"
            )

    months = list("JFMAMJJASOND")

    # Geometry
    col_w = img_size + gap_x
    row_h = img_size + gap_y

    # Extra room for month letters and side day numbers
    width = margin_left + 12 * col_w + margin_left
    height = margin_top + 31 * row_h + 40

    def href_for(idx: int, waning: bool = False) -> str:
        fname = theme_obj.image_filename(idx, waning)
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
    if font_style:
        parts.append(font_style)
    parts.append(f'<rect width="100%" height="100%" fill="{bg_color}"/>')

    # Title
    parts.append(
        f'<text x="{width/2:.1f}" y="32" text-anchor="middle" '
        f'font-family="\'{font_family}\', serif" font-size="32" fill="{fg_color}">{year}</text>'
    )

    # Month letters
    for m, letter in enumerate(months, start=1):
        x = margin_left + (m - 1) * col_w + img_size / 2
        parts.append(
            f'<text x="{x:.1f}" y="{margin_top-18}" text-anchor="middle" '
            f'font-family="\'{font_family}\', sans-serif" font-size="16" fill="{fg_color}">{letter}</text>'
        )

    # Day numbers left & right
    for day in range(1, 32):
        y = margin_top + (day - 1) * row_h + img_size * 0.75
        parts.append(
            f'<text x="{margin_left-18}" y="{y:.1f}" text-anchor="end" '
            f'font-family="\'{font_family}\', sans-serif" font-size="16" fill="{fg_color}">{day}</text>'
        )
        parts.append(
            f'<text x="{width-(margin_left-18)}" y="{y:.1f}" text-anchor="start" '
            f'font-family="\'{font_family}\', sans-serif" font-size="16" fill="{fg_color}">{day}</text>'
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

            # Get image index and flip flag from theme
            use_idx, flip = theme_obj.get_image_index(frac)

            # Determine if waning for themes with separate waning images
            is_waning = frac > 0.5

            x = margin_left + (month - 1) * col_w
            y = margin_top + (day - 1) * row_h
            cx = x + img_size / 2
            cy = y + img_size / 2

            # Get href based on theme type
            if theme_obj.has_waning_images:
                href = href_for(use_idx, waning=is_waning)
            else:
                href = href_for(use_idx, waning=False)

            # Calculate rotation if latitude provided
            tilt = 0.0
            if latitude is not None:
                tilt = moon_tilt_angle(d, latitude)

            # Build transform
            transforms = []
            if flip:
                transforms.append(f"translate({cx},{cy}) scale(-1,1) translate({-cx},{-cy})")
            if tilt != 0:
                transforms.append(f"rotate({tilt:.1f},{cx:.1f},{cy:.1f})")

            if transforms:
                transform_str = " ".join(transforms)
                parts.append(
                    f'<g transform="{transform_str}">'
                    f'<image href="{href}" x="{x}" y="{y}" '
                    f'width="{img_size}" height="{img_size}" />'
                    f'</g>'
                )
            else:
                parts.append(
                    f'<image href="{href}" x="{x}" y="{y}" '
                    f'width="{img_size}" height="{img_size}" />'
                )

    parts.append("</svg>")

    out_svg.write_text("\n".join(parts), encoding="utf-8")

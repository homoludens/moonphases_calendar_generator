"""Theme configuration for moon phase calendars."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Theme:
    """Configuration for a moon phase theme.

    Attributes:
        name: Theme identifier
        ext: File extension (e.g., ".jpg" or ".png")
        bg_color: Background color for calendar
        fg_color: Foreground/text color
        prefix: Filename prefix for images
        waning_prefix: Filename prefix for waning (full->new) images.
                       If None and not continuous, waxing images are mirrored.
        max_index: Maximum image index for waxing (0 to max_index inclusive)
        continuous: If True, images form a continuous sequence for full lunar cycle
                    (e.g., 0=new, 8=full, 15=almost new again). No mirroring.
        full_moon_index: Index of full moon image (only used if continuous=True)
    """

    name: str
    ext: str
    bg_color: str = "#000000"
    fg_color: str = "#ffffff"
    prefix: str = ""
    waning_prefix: str | None = None  # None means mirror (unless continuous)
    max_index: int = 14
    continuous: bool = False  # If True, images cover full cycle without mirroring
    full_moon_index: int = 7  # Index of full moon (for continuous themes)

    @property
    def has_waning_images(self) -> bool:
        """Whether theme has dedicated waning phase images."""
        return self.waning_prefix is not None

    @property
    def total_images(self) -> int:
        """Total number of images in the theme."""
        if self.continuous:
            return self.max_index + 1
        return self.max_index + 1  # Per phase

    def get_image_index(self, phase_fraction: float) -> tuple[int, bool]:
        """Get image index and flip flag for a given phase fraction.

        Args:
            phase_fraction: Moon phase as fraction [0, 1)
                           0.0 = new moon, 0.5 = full moon

        Returns:
            Tuple of (image_index, should_flip)
        """
        if self.continuous:
            # Direct mapping: phase 0->1 maps to index 0->max_index->0
            idx = int(round(phase_fraction * self.max_index)) % (self.max_index + 1)
            return idx, False

        # Separate waxing/waning handling
        is_waning = phase_fraction > 0.5

        if is_waning:
            # Waning: 0.5->1.0 maps to max_index->0
            phase_in_half = (phase_fraction - 0.5) * 2  # 0 to 1
            idx = int(round((1 - phase_in_half) * self.max_index))
        else:
            # Waxing: 0->0.5 maps to 0->max_index
            phase_in_half = phase_fraction * 2  # 0 to 1
            idx = int(round(phase_in_half * self.max_index))

        idx = max(0, min(self.max_index, idx))

        # Determine if flip needed
        if self.has_waning_images:
            flip = False
        else:
            flip = is_waning

        return idx, flip

    def image_filename(self, idx: int, waning: bool = False) -> str:
        """Get filename for a moon phase image.

        Args:
            idx: Image index
            waning: True for waning phase (only used if has_waning_images)

        Returns:
            Filename string
        """
        if waning and self.has_waning_images:
            return f"{self.waning_prefix}{idx}{self.ext}"
        return f"{self.prefix}{idx}{self.ext}"

    def image_path(self, image_dir: Path, idx: int, waning: bool = False) -> Path:
        """Get the full path to an image file."""
        return image_dir / self.image_filename(idx, waning)


# Built-in theme definitions
THEMES: dict[str, Theme] = {
    "white": Theme(
        name="white",
        ext=".jpg",
        bg_color="#000000",
        fg_color="#ffffff",
        prefix="d_150_",
        waning_prefix="u_150_",  # Has dedicated waning images
        max_index=14,
        continuous=False,
    ),
    "yellow": Theme(
        name="yellow",
        ext=".png",
        bg_color="#000000",
        fg_color="#dccfa1",
        prefix="",
        max_index=15,  # 0-15: 16 images for full cycle
        continuous=True,  # Continuous sequence, no mirroring
        full_moon_index=8,  # Image 8 is full moon
    ),
}

DEFAULT_THEME = "white"


def get_theme(name: str) -> Theme:
    """Get a theme by name."""
    if name not in THEMES:
        available = ", ".join(THEMES.keys())
        raise ValueError(f"Unknown theme '{name}'. Available themes: {available}")
    return THEMES[name]


def list_themes() -> list[str]:
    """Return list of available theme names."""
    return list(THEMES.keys())


def resolve_theme_dir(base_dir: Path, theme_name: str) -> Path:
    """Resolve the image directory for a theme."""
    theme_dir = base_dir / f"theme_{theme_name}"
    if theme_dir.is_dir():
        return theme_dir
    return base_dir

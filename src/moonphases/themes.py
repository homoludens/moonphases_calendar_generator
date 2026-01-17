"""Theme configuration for moon phase calendars."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Theme:
    """Configuration for a moon phase theme.

    Attributes:
        name: Theme identifier
        ext: File extension (e.g., ".jpg" or ".png")
        bg_color: Background color for calendar
        fg_color: Foreground/text color
        waxing_prefix: Filename prefix for waxing (new->full) images
        waning_prefix: Filename prefix for waning (full->new) images.
                       If None, waxing images are mirrored for waning phase.
        max_index: Maximum image index (0 to max_index inclusive)
    """

    name: str
    ext: str
    bg_color: str = "#000000"
    fg_color: str = "#ffffff"
    waxing_prefix: str = ""
    waning_prefix: str | None = None  # None means mirror waxing images
    max_index: int = 14  # Number of images per phase (0 to max_index)

    @property
    def has_waning_images(self) -> bool:
        """Whether theme has dedicated waning phase images."""
        return self.waning_prefix is not None

    def image_filename(self, idx: int, waning: bool = False) -> str:
        """Get filename for a moon phase image.

        Args:
            idx: Image index (0 to max_index)
            waning: True for waning phase (full->new)

        Returns:
            Filename string
        """
        if waning and self.has_waning_images:
            return f"{self.waning_prefix}{idx}{self.ext}"
        return f"{self.waxing_prefix}{idx}{self.ext}"

    def image_path(self, image_dir: Path, idx: int, waning: bool = False) -> Path:
        """Get the full path to an image file.

        Args:
            image_dir: Directory containing images
            idx: Image index
            waning: True for waning phase

        Returns:
            Full path to image file
        """
        return image_dir / self.image_filename(idx, waning)


# Built-in theme definitions
THEMES: dict[str, Theme] = {
    "white": Theme(
        name="white",
        ext=".jpg",
        bg_color="#000000",
        fg_color="#ffffff",
        waxing_prefix="d_150_",
        waning_prefix="u_150_",  # Has dedicated waning images
        max_index=14,
    ),
    "yellow": Theme(
        name="yellow",
        ext=".png",
        bg_color="#000000",
        fg_color="#ffffff",
        waxing_prefix="",
        waning_prefix=None,  # Mirror waxing images for waning
        max_index=15,
    ),
}

DEFAULT_THEME = "white"


def get_theme(name: str) -> Theme:
    """Get a theme by name.

    Args:
        name: Theme name (e.g., "white", "yellow")

    Returns:
        Theme configuration

    Raises:
        ValueError: If theme is not found
    """
    if name not in THEMES:
        available = ", ".join(THEMES.keys())
        raise ValueError(f"Unknown theme '{name}'. Available themes: {available}")
    return THEMES[name]


def list_themes() -> list[str]:
    """Return list of available theme names."""
    return list(THEMES.keys())


def resolve_theme_dir(base_dir: Path, theme_name: str) -> Path:
    """Resolve the image directory for a theme.

    Checks for theme subdirectory first, falls back to base_dir.

    Args:
        base_dir: Base images directory
        theme_name: Theme name

    Returns:
        Path to theme's image directory
    """
    theme_dir = base_dir / f"theme_{theme_name}"
    if theme_dir.is_dir():
        return theme_dir
    return base_dir

"""Theme configuration for moon phase calendars."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Theme:
    """Configuration for a moon phase theme."""

    name: str
    prefix: str  # Filename prefix (e.g., "d_150_" or "")
    ext: str  # File extension (e.g., ".jpg" or ".png")
    bg_color: str  # Background color
    fg_color: str  # Foreground/text color

    def image_path(self, image_dir: Path, idx: int) -> Path:
        """Get the path to an image file for the given index."""
        return image_dir / f"{self.prefix}{idx}{self.ext}"


# Built-in theme definitions
THEMES: dict[str, Theme] = {
    "white": Theme(
        name="white",
        prefix="d_150_",
        ext=".jpg",
        bg_color="#000000",
        fg_color="#ffffff",
    ),
    "yellow": Theme(
        name="yellow",
        prefix="",
        ext=".png",
        bg_color="#000000",
        fg_color="#ffffff",
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

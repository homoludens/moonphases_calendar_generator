# Moon Phases Calendar

Generate prinable SVG calendars showing moon phases for any year using only python standard library.


Example

![moon phase 2026 calendar](images/moon_calendar_2026_2.png)

## Installation

```bash
pip install -e .
```

## Usage

### 1. Download moon phase images

```bash
moonphases download -o images
```

This downloads 15 moon phase images (new moon to full moon) from astro-seek.com.

### 2. Generate calendar SVG

```bash
moonphases generate 2027 -i images -o moon_calendar_2027.svg
```

Options:
- `-i, --images`: Directory containing moon phase images (default: `images`)
- `-o, --output`: Output SVG file (default: `moon_calendar_YEAR.svg`)
- `--img-size`: Size of moon images in pixels (default: 30)

## Project Structure

```
moonphases/
├── src/moonphases/
│   ├── __init__.py
│   ├── __main__.py    # CLI entry point
│   ├── calendar.py    # SVG generation
│   └── downloader.py  # Image downloading
├── images/            # Moon phase images
├── pyproject.toml
└── README.md
```

## How it works

The calendar calculates moon phases using the synodic month (29.53 days) from a reference new moon date. Each day is mapped to one of 15 moon phase images, with waning phases created by horizontally flipping the waxing images.

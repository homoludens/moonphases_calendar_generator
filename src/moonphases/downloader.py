"""Download moon phase images from astro-seek.com."""

from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}


def download_image(url: str, output_dir: Path) -> Path:
    """Download an image from URL to output directory."""
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=10) as response:
        data = response.read()

    filename = Path(urlparse(url).path).name
    output_path = output_dir / filename

    with open(output_path, "wb") as f:
        f.write(data)

    return output_path


def download_moon_images(output_dir: Path, count: int = 15, size: int = 150) -> list[Path]:
    """
    Download moon phase images from astro-seek.com.

    Args:
        output_dir: Directory to save images
        count: Number of images to download (default 15 for half cycle)
        size: Image size (50 or 150)

    Returns:
        List of downloaded file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded = []

    for i in range(count):
        url = f"https://www.astro-seek.com/seek-images/lunarni_kalendar/d_{size}_{i}.jpg"
        print(f"Downloading: {url}")
        path = download_image(url, output_dir)
        downloaded.append(path)

    return downloaded

"""Convert SVG to PDF using Playwright."""

from pathlib import Path

from playwright.sync_api import sync_playwright


def svg_to_pdf(
    svg_path: Path,
    pdf_path: Path | None = None,
    page_format: str = "A3",
    background_color: str = "black",
) -> Path:
    """
    Convert an SVG file to PDF using Playwright/Chromium.

    Args:
        svg_path: Path to the input SVG file
        pdf_path: Path for the output PDF file (default: same name as SVG with .pdf extension)
        page_format: PDF page format (e.g., "A3", "A4", "Letter")
        background_color: Background color for the PDF

    Returns:
        Path to the generated PDF file
    """
    svg_path = Path(svg_path)
    if pdf_path is None:
        pdf_path = svg_path.with_suffix(".pdf")
    else:
        pdf_path = Path(pdf_path)

    # Generate the absolute directory URL for resolving relative image paths
    base_dir_url = svg_path.parent.resolve().as_uri() + "/"

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # Set the base_url for resolving relative paths in the SVG
        context = browser.new_context(base_url=base_dir_url)
        page = context.new_page()

        svg_content = svg_path.read_text(encoding="utf-8")

        # Wrap SVG in HTML so CSS styling works
        page.set_content(f"""
        <html>
            <head>
                <style>
                    body, html {{ margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; background-color: {background_color};}}
                    svg {{ display: block; height: 100vh; width: auto; margin: 0 auto; }}
                </style>
            </head>
            <body>
                {svg_content}
            </body>
        </html>
        """)

        # Wait for local images to finish loading
        page.wait_for_load_state("networkidle")

        page.pdf(
            path=str(pdf_path),
            format=page_format,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"}
        )

        context.close()
        browser.close()

    return pdf_path

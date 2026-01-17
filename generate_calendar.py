#!/usr/bin/env python3
"""Generate moon phase calendar without installing the package.

Usage:
    python generate_calendar.py 2027 -i moonphases -t white --lat 45
    python generate_calendar.py 2027 -i moonphases -t yellow -o my_calendar.svg
"""

import sys
from pathlib import Path

# Add src to path so we can import without installing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from moonphases.__main__ import main

if __name__ == "__main__":
    main()

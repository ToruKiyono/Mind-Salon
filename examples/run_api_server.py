from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mind_salon.api import run_api_server


if __name__ == "__main__":
    run_api_server(host="127.0.0.1", port=8000)

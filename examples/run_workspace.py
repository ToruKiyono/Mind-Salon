from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"
API_SCRIPT = ROOT / "examples" / "run_api_server.py"


def _start_process(args: list[str], cwd: Path | None = None) -> subprocess.Popen:
    return subprocess.Popen(args, cwd=str(cwd) if cwd else None)


def _find_frontend_runner() -> list[str]:
    candidates = [
        ["npm.cmd", "run", "dev"],
        ["npm", "run", "dev"],
        ["pnpm.cmd", "dev"],
        ["pnpm", "dev"],
        ["yarn.cmd", "dev"],
        ["yarn", "dev"],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            return cmd
    raise SystemExit("No frontend runner found. Install Node.js and ensure npm/pnpm/yarn is in PATH.")


def main() -> int:
    if not (FRONTEND_DIR / "node_modules").exists():
        raise SystemExit("Missing frontend dependencies. Run: cd frontend && npm install")

    api_proc = _start_process([sys.executable, str(API_SCRIPT)], cwd=ROOT)
    print("Started API: http://127.0.0.1:8000")
    time.sleep(0.4)

    frontend_proc = _start_process(_find_frontend_runner(), cwd=FRONTEND_DIR)
    print("Started Frontend: http://127.0.0.1:5173")
    print("Tip: open http://127.0.0.1:5173?apiBase=http://127.0.0.1:8000")

    try:
        return frontend_proc.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        for proc in (frontend_proc, api_proc):
            if proc.poll() is None:
                proc.terminate()
        time.sleep(0.2)
        for proc in (frontend_proc, api_proc):
            if proc.poll() is None:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())

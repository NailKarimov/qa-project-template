"""Mutation check: plant one bug at a time and make sure the suite fails.

    python scripts/mutants.py            # all mutants, memory:// transport
    BUS_URL=socat:// python scripts/mutants.py

Writes ``mutants-result.md``. Exit code 1 if any mutant survives.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# id, file, original text, mutated text, what the bug means
MUTANTS = [
    ("M1", "src/bus_lab/crc.py", "INIT = 0xFFFF", "INIT = 0x0000", "CRC starts from 0 instead of 0xFFFF"),
    ("M2", "src/bus_lab/crc.py", "POLY = 0xA001", "POLY = 0x8005", "CRC uses the non-reflected polynomial"),
    ("M3", "src/bus_lab/crc.py", 'to_bytes(2, "little")', 'to_bytes(2, "big")', "CRC sent high byte first"),
    (
        "M4",
        "src/bus_lab/frame.py",
        "if len(raw) != expected:",
        "if len(raw) < expected:",
        "trailing bytes after a frame are accepted",
    ),
    (
        "M5",
        "src/bus_lab/frame.py",
        "if len(self.payload) > MAX_PAYLOAD:",
        "if len(self.payload) > MAX_PAYLOAD + 1:",
        "payload limit off by one",
    ),
    (
        "M6",
        "src/bus_lab/device.py",
        "if frame.address != self.address:\n            return None",
        "if False:\n            return None",
        "device answers every address",
    ),
    (
        "M7",
        "src/bus_lab/device.py",
        "self.broadcasts += 1\n            return None",
        "self.broadcasts += 1\n            return encode(Frame(self.address, frame.payload))",
        "device answers a broadcast",
    ),
    (
        "M8",
        "src/bus_lab/device.py",
        "self.framing_errors += 1\n                self.transport.reset_input()",
        "self.framing_errors += 1",
        "input not flushed after a framing error",
    ),
]


def run_suite(workdir: Path) -> bool:
    """True if the suite passes."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "-m", "not hardware"],
        cwd=workdir,
        env=env,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main() -> int:
    rows = []
    survived = 0
    with tempfile.TemporaryDirectory() as tmp:
        for mid, rel, old, new, meaning in MUTANTS:
            work = Path(tmp) / mid
            shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".venv", "__pycache__", ".git", "allure-*"))
            target = work / rel
            text = target.read_text()
            if text.count(old) != 1:
                print(f"{mid}: pattern not found exactly once in {rel}", file=sys.stderr)
                return 2
            target.write_text(text.replace(old, new))
            caught = not run_suite(work)
            survived += not caught
            rows.append(f"| {mid} | `{rel}` | {meaning} | {'caught' if caught else '**survived**'} |")
            print(f"{mid}: {'caught' if caught else 'SURVIVED'} — {meaning}")

    total = len(MUTANTS)
    report = [
        "# Mutation check",
        "",
        f"{total - survived}/{total} planted bugs caught (transport: {os.getenv('BUS_URL', 'memory://')}).",
        "",
        "| Id | File | Planted bug | Result |",
        "| --- | --- | --- | --- |",
        *rows,
        "",
    ]
    (ROOT / "mutants-result.md").write_text("\n".join(report))
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())

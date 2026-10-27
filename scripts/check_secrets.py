#!/usr/bin/env python3
"""Catch common credential and private-key patterns in public catalog content."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "data", ROOT / "site" / "catalog", ROOT / "api-connector.request.json", ROOT / "api-connector.manifest.json"]
PATTERNS = {
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "OpenAI-style secret key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key header": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential assignment": re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{20,}"),
}


def main() -> int:
    findings = []
    files = []
    for target in TARGETS:
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(path for path in target.rglob("*") if path.is_file())
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        for name, pattern in PATTERNS.items():
            match = pattern.search(text)
            if match:
                findings.append(f"{path.relative_to(ROOT)}: possible {name}")
    if findings:
        print("Potential secrets detected:", file=sys.stderr)
        print("\n".join(findings), file=sys.stderr)
        return 1
    print(f"Secret scan clear ({len(files)} public-data files scanned).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Disable upstream bootstrap download after the custom bootstrap is staged."""
from pathlib import Path
import re
import sys

gradle = Path(sys.argv[1])
text = gradle.read_text(encoding="utf-8")
pattern = r'(def\s+downloadBootstrap\s*\([^)]*\)\s*\{\s*)'
patched, n = re.subn(pattern, r'\1return\n', text, count=1)
if n != 1:
    raise SystemExit("Could not locate downloadBootstrap() in app/build.gradle; upstream changed.")
gradle.write_text(patched, encoding="utf-8")
print("Disabled remote default bootstrap download; using staged custom bootstrap archives.")

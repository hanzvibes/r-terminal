#!/usr/bin/env python3
"""Apply narrowly-scoped R-Terminal branding to a checked-out Termux source tree."""
from pathlib import Path
import os
import re
import sys

root = Path(sys.argv[1]).resolve()
package = os.environ.get("TERMUX_PACKAGE_NAME", "id.rworks.rterminal")
app_name = os.environ.get("TERMUX_APP_NAME", "R-Terminal")

if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+", package):
    raise SystemExit(f"Invalid Android application ID: {package}")

constants = root / "termux-shared/src/main/java/com/termux/shared/termux/TermuxConstants.java"
gradle = root / "app/build.gradle"
if not constants.exists() or not gradle.exists():
    raise SystemExit("Upstream layout changed: expected TermuxConstants.java and app/build.gradle")

def replace_once(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one occurrence in {path}: {old!r}; found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_once(constants,
    'public static final String TERMUX_APP_NAME = "Termux";',
    f'public static final String TERMUX_APP_NAME = "{app_name}";')
replace_once(constants,
    'public static final String TERMUX_PACKAGE_NAME = "com.termux";',
    f'public static final String TERMUX_PACKAGE_NAME = "{package}";')

gradle_text = gradle.read_text(encoding="utf-8")
gradle_text, count = re.subn(
    r'(?m)^\s*applicationId\s+"com\.termux"\s*$',
    f'        applicationId "{package}"',
    gradle_text,
    count=1,
)
if count != 1:
    raise SystemExit("Could not uniquely patch applicationId in app/build.gradle")
gradle.write_text(gradle_text, encoding="utf-8")

# App display label is resolved from the app's strings resource.
strings_candidates = [
    root / "app/src/main/res/values/strings.xml",
    root / "app/src/main/res/values/strings.xml",
]
strings = next((p for p in strings_candidates if p.exists()), None)
if strings:
    xml = strings.read_text(encoding="utf-8")
    xml2, n = re.subn(
        r'(<string\s+name="app_name"\s*>).*?(</string>)',
        lambda m: m.group(1) + app_name + m.group(2),
        xml,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("Could not patch app_name string resource")
    strings.write_text(xml2, encoding="utf-8")

print(f"Patched Termux as {app_name} ({package})")

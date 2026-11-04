#!/usr/bin/env python3
"""Apply the R-Terminal package identity to a pinned Termux source checkout."""
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
if not constants.is_file() or not gradle.is_file():
    raise SystemExit("Pinned Termux layout changed: expected TermuxConstants.java and app/build.gradle")

def replace_once(path: Path, old: str, new: str):
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Expected one match in {path}: {old!r}; found {count}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")

replace_once(constants,
    'public static final String TERMUX_APP_NAME = "Termux"; // Default: "Termux"',
    f'public static final String TERMUX_APP_NAME = "{app_name}"; // R-Terminal')
replace_once(constants,
    'public static final String TERMUX_PACKAGE_NAME = "com.termux"; // Default: "com.termux"',
    f'public static final String TERMUX_PACKAGE_NAME = "{package}"; // R-Terminal')

gradle_text = gradle.read_text(encoding="utf-8")
rules = [
    (r'(?m)^(\s*applicationId\s+)"com\.termux"(\s*)$', rf'\g<1>"{package}"\g<2>', "applicationId"),
    (r'(?m)^(\s*manifestPlaceholders\.TERMUX_PACKAGE_NAME\s*=\s*)"com\.termux"(\s*)$', rf'\g<1>"{package}"\g<2>', "manifest package placeholder"),
    (r'(?m)^(\s*manifestPlaceholders\.TERMUX_APP_NAME\s*=\s*)"Termux"(\s*)$', rf'\g<1>"{app_name}"\g<2>', "manifest app-name placeholder"),
    (r"(?m)^\s*include 'x86', 'x86_64', 'armeabi-v7a', 'arm64-v8a'\s*$", "                include 'arm64-v8a'", "ABI split list"),
]
for pattern, replacement, label in rules:
    gradle_text, count = re.subn(pattern, replacement, gradle_text, count=1)
    if count != 1:
        raise SystemExit(f"Could not uniquely patch {label} in app/build.gradle")
gradle.write_text(gradle_text, encoding="utf-8")

for relative in (
    "app/src/main/res/values/strings.xml",
    "termux-shared/src/main/res/values/strings.xml",
):
    resource = root / relative
    if not resource.is_file():
        raise SystemExit(f"Missing expected upstream resource: {relative}")
    replace_once(resource,
        '<!ENTITY TERMUX_APP_NAME "Termux">',
        f'<!ENTITY TERMUX_APP_NAME "{app_name}">')

print(f"Patched Termux identity: {app_name} ({package}), ABI arm64-v8a")

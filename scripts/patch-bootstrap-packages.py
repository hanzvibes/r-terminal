#!/usr/bin/env python3
"""Apply a build-only compatibility patch to Termux's ncurses bootstrap recipe.

The pinned foot archive currently fails its upstream SHA-256 check from Codeberg.
Foot's terminfo entry is optional for R-Terminal, so omit only that optional
terminfo source. The optional pyunbound Python binding is also disabled: the
ARM64 bootstrap needs native libunbound, not its SWIG-generated Python wrapper.
All remaining source downloads keep their original checksums.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
recipe = root / "packages/ncurses/build.sh"
text = recipe.read_text()

replacements = [
    (
        '''                    "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_VERSION")"
                    "$(. "$TERMUX_SCRIPTDIR/x11-packages/foot/build.sh"; echo "$TERMUX_PKG_VERSION")")''',
        '''                    "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_VERSION")")''',
    ),
    (
        '''                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_SRCURL")"
                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/foot/build.sh"; echo "$TERMUX_PKG_SRCURL")")''',
        '''                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_SRCURL")")''',
    ),
    (
        '''                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_SHA256")"
                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/foot/build.sh"; echo "$TERMUX_PKG_SHA256")")''',
        '''                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_SHA256")")''',
    ),
]

for before, after in replacements:
    count = text.count(before)
    if count != 1:
        raise SystemExit(f"Expected exactly one patch target, found {count}")
    text = text.replace(before, after, 1)

lines = text.splitlines(keepends=True)
markers = [i for i, line in enumerate(lines) if line.strip() == "# Upstream instructions for building foot's terminfo"]
if len(markers) != 1:
    raise SystemExit(f"Expected one optional foot terminfo block, found {len(markers)}")
start = markers[0]
block = lines[start:start + 4]
if len(block) != 4 or "tic -x -e foot,foot-direct" not in block[-1]:
    raise SystemExit("Optional foot terminfo block did not match expected upstream layout")
del lines[start:start + 4]
text = "".join(lines)

if "x11-packages/foot/build.sh" in text or "foot/foot.info" in text:
    raise SystemExit("Foot source reference remains after patch")
recipe.write_text(text)
print(f"Patched optional foot terminfo source out of {recipe}")

# The bootstrap needs native libunbound, not its optional Python binding.
# Disabling pyunbound avoids a SWIG-generated wrapper containing an unexpanded
# $function token with the builder's SWIG 4.5.1.
unbound_recipe = root / "packages/libunbound/build.sh"
unbound_text = unbound_recipe.read_text()
for line in (
    'TERMUX_PKG_BUILD_DEPENDS="python, swig"\n',
    'TERMUX_PKG_PYTHON_COMMON_DEPS="wheel"\n',
    'TERMUX_PKG_PYTHON_BUILD_DEPS="swig"\n',
):
    count = unbound_text.count(line)
    if count != 1:
        raise SystemExit(f"Expected one optional Python build setting in {unbound_recipe}, found {count}: {line.strip()}")
    unbound_text = unbound_text.replace(line, "", 1)
if unbound_text.count("--with-pyunbound") != 1:
    raise SystemExit("Expected exactly one --with-pyunbound option")
unbound_text = unbound_text.replace("--with-pyunbound", "--without-pyunbound", 1)
unbound_recipe.write_text(unbound_text)
print(f"Disabled optional pyunbound binding in {unbound_recipe}")

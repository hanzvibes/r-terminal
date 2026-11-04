#!/usr/bin/env python3
"""Apply a build-only compatibility patch to Termux's ncurses bootstrap recipe.

The pinned foot archive currently fails its upstream SHA-256 check from Codeberg.
Foot's terminfo entry is optional for R-Terminal, so omit only that optional
terminfo source. All remaining source downloads keep their original checksums.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
recipe = root / "packages/ncurses/build.sh"
text = recipe.read_text()

replacements = [
    (
        '                    "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_VERSION")"\n'
        '                    "$(. "$TERMUX_SCRIPTDIR/x11-packages/foot/build.sh"; echo "$TERMUX_PKG_VERSION")")',
        '                    "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_VERSION")")',
    ),
    (
        '                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_SRCURL")"\n'
        '                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/foot/build.sh"; echo "$TERMUX_PKG_SRCURL")")',
        '                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_SRCURL")")',
    ),
    (
        '                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_SHA256")"\n'
        '                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/foot/build.sh"; echo "$TERMUX_PKG_SHA256")")',
        '                   "$(. "$TERMUX_SCRIPTDIR/x11-packages/alacritty/build.sh"; echo "$TERMUX_PKG_SHA256")")',
    ),
    (
        '\t# Upstream instructions for building foot\'s terminfo\n'
        '\t# See: https://codeberg.org/dnkl/foot/src/branch/master/INSTALL.md#terminfo\n'
        '\tsed \'s/@default_terminfo@/foot/g\' "$TERMUX_PKG_SRCDIR/foot/foot.info" | \\\n'
        '\t\ttic -x -e foot,foot-direct -o "$TI" -\n',
        '',
    ),
]

for before, after in replacements:
    count = text.count(before)
    if count != 1:
        raise SystemExit(f"Expected exactly one patch target, found {count}: {before[:100]!r}")
    text = text.replace(before, after, 1)

if "x11-packages/foot/build.sh" in text or "foot/foot.info" in text:
    raise SystemExit("Foot source reference remains after patch")
recipe.write_text(text)
print(f"Patched optional foot terminfo source out of {recipe}")

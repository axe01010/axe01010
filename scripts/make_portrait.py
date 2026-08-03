#!/usr/bin/env python3
"""Generate a large ASCII-art portrait SVG from a source image.

Renders a character-ramp shaded portrait (dark bg, green accents) with a
SMIL reveal animation, matching the portfolio brand palette.
"""

import argparse
from pathlib import Path

from PIL import Image

# Character ramp: quiet (dark) -> loud (bright)
RAMP = " .`:-=+*cs#%@"
# RAMP = " .:-=+*#%@"


def ramp_index(v: float) -> int:
    """Map 0..1 brightness to a ramp index."""
    idx = int(v * (len(RAMP) - 1))
    return max(0, min(len(RAMP) - 1, idx))


def make_portrait(src: str = "/tmp/art_source.png", out: str = "ascii.svg",
                  cols: int = 120, cell: int = 6, animate: bool = True):
    img = Image.open(src).convert("L")
    # target aspect: keep source ratio
    rows = max(1, int(cols * img.height / img.width * 0.5))
    img = img.resize((cols, rows))

    px = img.load()
    width = cols * cell
    height = rows * cell

    lines = []
    for y in range(rows):
        line = ""
        for x in range(cols):
            v = px[x, y] / 255.0
            line += RAMP[build_index(v)]
        lines.append(line)

    # SVG
    ns = "http://www.w3.org/2000/svg"
    parts = []
    parts.append(
        f'<svg xmlns="{ns}" viewBox="0 0 {width} {height}" '
        f'width="{width*8}" height="{leight*8}" '
        f'style="background:#080b10">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="#080b10"/>')

    # per-cell text with green brand gradient by brightness
    for y, line in enumerate(lines):
        for x, ch in enumerate(line):
            if ch == " ":
                continue
            v = px[x, y] / 255.0
            r = int(8 + 30 * v)
            g = int(50 + 140 * v)
            b = int(40 + 70 * v)
            color = f"#{r:02x}{g:02x}{b:02x}"
            tx = x * cell
            ty = y * cell + cell - 1
            parts.append(
                f'<text x="{tx}" y="{ty}" fill="{color}" '
                f'font-family="monospace" font-size="{cell-1}" '
                f'font-weight="bold">{ch}</text>'
            )

    if animate:
        # SMIL self-typing reveal: fade in columns left->right
        dur = 3.0
        parts.append(
            f'<rect width="{width}" height="{height}" fill="#080b10">'
            f'<animate attributeName="width" from="{width}" to="0" '
            f'dur="{dur}s" begin="0s" fill="freeze"/></rect>'
        )

    parts.append("</svg>")
    Path(out).write_text("\n".join(parts))
    print(f"Wrote {out} ({cols}x{rows}, {width}x{height})")


def build_index(v: float) -> int:
    return int(v * (len(RAMP) - 1))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--src", default="/tmp/art_source.png")
    p.add_argument("--out", default="ascii.svg")
    p.add_argument("--cols", type=int, default=100)
    p.add_argument("--no-animate", action="store_true")
    a = p.parse_args()
    make_portrait(a.src, a.out, a.cols, animate=not a.no_animate)

#!/usr/bin/env python3
"""Generate ASCII art portrait SVG from a text grid."""

import xml.etree.ElementTree as ET
from pathlib import Path

# Arch Linux logo ASCII art (simplified)
ARCH_ASCII = [
    "    .__",
    "   /  `.",
    "  |     |",
    "   \\___/",
    "  /|   |\\",
    " | |   | |",
    "  \\|   |/",
    "   `---'",
]

# Character ramp: quiet to loud
RAMP = [":", "+", "#", "@"]


def make_portrait(output_path: str = "ascii.svg"):
    rows = len(ARCH_ASCII)
    cols = max(len(r) for r in ARCH_ASCII)
    cell_w = 6
    cell_h = 6
    width = cols * cell_w
    height = rows * cell_h

    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    svg = ET.Element(
        "svg",
        {
            "xmlns": ns,
            "viewBox": f"0 0 {width} {height}",
            "width": str(width * 8),
            "height": str(height * 8),
        },
    )

    # Background
    bg = ET.SubElement(
        svg, "rect", {"width": str(width), "height": str(height), "fill": "#0f0f23"}
    )

    for row_idx, line in enumerate(ARCH_ASCII):
        for col_idx, ch in enumerate(line):
            if ch == " ":
                continue
            x = col_idx * cell_w
            y = row_idx * cell_h + cell_h - 1
            # Map character to ramp index
            ramp_idx = min(RAMP.index(ch) if ch in RAMP else 1, len(RAMP) - 1)
            color_intensity = 40 + ramp_idx * 55
            color = f"#1793d1"
            ET.SubElement(
                svg,
                "text",
                {
                    "x": str(x),
                    "y": str(y),
                    "fill": color,
                    "font-family": "monospace",
                    "font-size": str(cell_h - 1),
                    "font-weight": "bold",
                },
            ).text = ch

    Path(output_path).write_text(ET.tostring(svg, encoding="unicode"))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    make_portrait()

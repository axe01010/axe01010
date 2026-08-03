#!/usr/bin/env python3
"""Generate profile SVG assets from GitHub GraphQL API."""

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests

USERNAME = os.environ.get("USERNAME", "axe01010")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Brand palette — matches portfolio-v2
BG = "#080b10"
SURFACE = "#0f1419"
BORDER = "#30363d"
TEXT = "#eef2f6"
MUTED = "#8b9aab"
ACCENT = "#2f6f4f"
ACCENT_BRIGHT = "#45a06e"

FEATURED = [
    ("nothing-phone-bootloop-recovery", "Android bootloop rescue via fastboot"),
    ("cursor-android-toolkit", "Cursor IDE/CLI on Termux + Ubuntu"),
    ("portfolio-v2", "Live portfolio — axe01010.github.io"),
    ("skills-orchestrator", "Cursor skills + design bundles"),
    ("security-research-hub", "Security research writeups"),
]

STACK = ["Python", "Android", "Fastboot", "Termux", "Cursor", "APK", "GitHub Actions"]

QUERY = """
query($login:String!){
  user(login:$login){
    login
    name
    bio
    location
    websiteUrl
    followers{totalCount}
    following{totalCount}
    repositories(ownerAffiliations:OWNER,first:100){
      totalCount
      nodes{name stargazerCount forkCount primaryLanguage{name}}
    }
    contributionsCollection{
      contributionYears
      totalCommitContributions
    }
  }
}
"""

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def fetch_graphql():
    headers = {"Authorization": f"bearer {TOKEN}"} if TOKEN else {}
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    if not payload.get("data", {}).get("user"):
        raise RuntimeError(payload)
    return payload["data"]["user"]


def _svg_root(width, height):
    svg = ET.Element("svg", {
        "xmlns": NS,
        "viewBox": f"0 0 {width} {height}",
        "width": str(width),
        "height": str(height),
    })
    ET.SubElement(svg, "rect", {
        "width": str(width), "height": str(height), "fill": BG, "rx": "10",
    })
    return svg


def _card(svg, width, height, rx=10):
    g = ET.SubElement(svg, "g")
    ET.SubElement(g, "rect", {
        "width": str(width), "height": str(height),
        "fill": SURFACE, "rx": str(rx),
        "stroke": BORDER, "stroke-width": "1",
    })
    return g


def _text(parent, x, y, content, *, fill=TEXT, size=10, bold=False, mono=True):
    el = ET.SubElement(parent, "text", {
        "x": str(x), "y": str(y),
        "fill": fill,
        "font-family": "monospace" if mono else "sans-serif",
        "font-size": str(size),
        "font-weight": "bold" if bold else "normal",
    })
    el.text = content
    return el


def _tspans(parent, x, y, lines, *, fill=TEXT, size=9):
    text = ET.SubElement(parent, "text", {
        "x": str(x), "y": str(y), "fill": fill,
        "font-family": "monospace", "font-size": str(size),
    })
    for i, line in enumerate(lines):
        t = ET.SubElement(text, f"{{{NS}}}tspan", {
            "x": str(x), "dy": "0" if i == 0 else "1.35em",
        })
        t.text = line
    return text


def write_svg(path, svg):
    Path(path).write_text(ET.tostring(svg, encoding="unicode"))
    print(f"Wrote {path}")


def make_banner(user, path="banner.svg"):
    w, h = 860, 130
    svg = _svg_root(w, h)
    # accent glow line
    ET.SubElement(svg, "rect", {
        "x": "24", "y": "24", "width": "4", "height": "82", "fill": ACCENT_BRIGHT, "rx": "2",
    })
    _text(svg, 44, 52, user.get("name") or user["login"], fill=ACCENT_BRIGHT, size=22, bold=True, mono=False)
    _text(svg, 44, 78, user.get("bio") or "Recovery guides and dev tooling", fill=MUTED, size=11, mono=False)
    loc = user.get("location") or "India"
    blog = user.get("websiteUrl") or "axe01010.github.io/portfolio-v2"
    _text(svg, 44, 100, f"{loc}  ·  {blog.replace('https://', '')}", fill=TEXT, size=9)
    # grid accent
    for i in range(0, w, 48):
        ET.SubElement(svg, "line", {
            "x1": str(i), "y1": "0", "x2": str(i), "y2": str(h),
            "stroke": BORDER, "stroke-width": "0.5", "opacity": "0.35",
        })
    write_svg(path, svg)


def make_stats_svg(user, repos, path="stats.svg"):
    w, h = 250, 155
    svg = _svg_root(w, h)
    _card(svg, w, h)
    stars = sum(r["stargazerCount"] for r in repos)
    forks = sum(r["forkCount"] for r in repos)
    lines = [
        f"Repos     {user['repositories']['totalCount']}",
        f"Stars     {stars}",
        f"Forks     {forks}",
        f"Followers {user['followers']['totalCount']}",
        f"Following {user['following']['totalCount']}",
    ]
    _text(svg, 14, 22, "Live stats", fill=ACCENT_BRIGHT, size=10, bold=True)
    _tspans(svg, 14, 42, lines, fill=TEXT, size=10)
    write_svg(path, svg)


def make_langs_svg(repos, path="langs.svg"):
    w, h = 250, 130
    svg = _svg_root(w, h)
    _card(svg, w, h)
    langs = {}
    for r in repos:
        pl = r.get("primaryLanguage")
        if pl:
            langs[pl["name"]] = langs.get(pl["name"], 0) + 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:5]
    lines = [f"{n:<12} {c}" for n, c in top] or ["(no language data)"]
    _text(svg, 14, 22, "Languages", fill=ACCENT_BRIGHT, size=10, bold=True)
    _tspans(svg, 14, 42, lines, fill=TEXT, size=10)
    write_svg(path, svg)


def make_streak_svg(user, path="streak.svg"):
    w, h = 250, 110
    svg = _svg_root(w, h)
    _card(svg, w, h)
    contrib = user.get("contributionsCollection") or {}
    years = contrib.get("contributionYears") or []
    current = years[-1] if years else datetime.now().year
    lines = [
        f"Year    {current}",
        f"Commits {contrib.get('totalCommitContributions', 0)}",
        f"Active  {len(years)} yrs",
    ]
    _text(svg, 14, 22, "Activity", fill=ACCENT_BRIGHT, size=10, bold=True)
    _tspans(svg, 14, 42, lines, fill=TEXT, size=10)
    write_svg(path, svg)


def make_year_svg(user, path="year.svg"):
    w, h = 250, 110
    svg = _svg_root(w, h)
    _card(svg, w, h)
    years = (user.get("contributionsCollection") or {}).get("contributionYears") or []
    lines = [str(y) for y in (years[-6:] or [datetime.now().year])]
    _text(svg, 14, 22, "Years", fill=ACCENT_BRIGHT, size=10, bold=True)
    _tspans(svg, 14, 42, lines, fill=TEXT, size=10)
    write_svg(path, svg)


def make_connect_svg(path="connect.svg"):
    w, h = 860, 56
    svg = _svg_root(w, h)
    links = [
        ("Portfolio", "axe01010.github.io/portfolio-v2"),
        ("Skills", "github.com/axe01010/skills-orchestrator"),
        ("Research", "github.com/axe01010/security-research-hub"),
        ("Android", "github.com/axe01010/cursor-android-toolkit"),
    ]
    x = 20
    for label, url in links:
        bw = len(label) * 7 + 24
        ET.SubElement(svg, "rect", {
            "x": str(x), "y": "14", "width": str(bw), "height": "28",
            "fill": SURFACE, "rx": "6", "stroke": ACCENT, "stroke-width": "1",
        })
        _text(svg, x + 12, 33, label, fill=ACCENT_BRIGHT, size=10, bold=True)
        x += bw + 12
    write_svg(path, svg)


def make_stack_svg(path="stack.svg"):
    w, h = 860, 72
    svg = _svg_root(w, h)
    _text(svg, 20, 24, "Stack", fill=ACCENT_BRIGHT, size=10, bold=True)
    x = 20
    for tech in STACK:
        bw = len(tech) * 7 + 20
        ET.SubElement(svg, "rect", {
            "x": str(x), "y": "36", "width": str(bw), "height": "26",
            "fill": SURFACE, "rx": "5", "stroke": BORDER, "stroke-width": "1",
        })
        _text(svg, x + 10, 53, tech, fill=TEXT, size=9)
        x += bw + 8
    write_svg(path, svg)


def make_featured_svg(path="featured.svg"):
    w, h = 860, 200
    svg = _svg_root(w, h)
    _text(svg, 20, 24, "Featured projects", fill=ACCENT_BRIGHT, size=11, bold=True)
    y = 44
    for name, desc in FEATURED:
        ET.SubElement(svg, "rect", {
            "x": "16", "y": str(y - 12), "width": str(w - 32), "height": "28",
            "fill": SURFACE, "rx": "6", "stroke": BORDER, "stroke-width": "1",
        })
        _text(svg, 28, y + 4, name, fill=ACCENT_BRIGHT, size=9, bold=True)
        _text(svg, 320, y + 4, desc, fill=MUTED, size=9)
        y += 32
    write_svg(path, svg)


def make_hd_svg(text, path, width=140, height=32):
    svg = _svg_root(width, height)
    ET.SubElement(svg, "rect", {
        "x": "8", "y": "24", "width": str(len(text) * 7 + 8), "height": "2",
        "fill": ACCENT, "rx": "1",
    })
    _text(svg, 10, 20, text, fill=TEXT, size=11, bold=True)
    write_svg(path, svg)


if __name__ == "__main__":
    user = fetch_graphql()
    repos = user["repositories"]["nodes"]
    make_banner(user)
    make_stats_svg(user, repos)
    make_langs_svg(repos)
    make_streak_svg(user)
    make_year_svg(user)
    make_connect_svg()
    make_stack_svg()
    make_featured_svg()
    make_hd_svg("About", "hd-about.svg", width=100)
    make_hd_svg("Stack", "hd-stack.svg", width=90)
    make_hd_svg("Projects", "hd-projects.svg", width=110)
    make_hd_svg("Stats", "hd-stats.svg", width=80)
    make_hd_svg("Connect", "hd-connect.svg", width=110)
    make_hd_svg("About this page", "hd-about-this-page.svg", width=170)

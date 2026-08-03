#!/usr/bin/env python3
"""Generate the full axe01010 profile SVG dashboard from config + GitHub GraphQL."""

import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "profile.config.json").read_text())
USERNAME = os.environ.get("USERNAME", CONFIG["handle"])
TOKEN = os.environ.get("GITHUB_TOKEN", "")

BG = "#080b10"
SURFACE = "#0f1419"
SURFACE_2 = "#141b22"
BORDER = "#30363d"
TEXT = "#eef2f6"
MUTED = "#8b9aab"
ACCENT = "#2f6f4f"
ACCENT_BRIGHT = "#45a06e"
GLOW = "rgba(47,111,79,0.22)"

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

QUERY = """
query($login:String!){
  user(login:$login){
    login name bio location websiteUrl
    followers{totalCount} following{totalCount}
    repositories(ownerAffiliations:OWNER,first:100,orderBy:{field:UPDATED_AT,direction:DESC}){
      totalCount
      nodes{name description stargazerCount forkCount url primaryLanguage{name}}
    }
    contributionsCollection{
      contributionYears
      totalCommitContributions
      contributionCalendar{
        totalContributions
        weeks{contributionDays{contributionCount date color}}
      }
    }
  }
}
"""


def fetch_user():
    headers = {"Authorization": f"bearer {TOKEN}"} if TOKEN else {}
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers=headers,
        timeout=45,
    )
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def svg_open(w, h):
    svg = ET.Element("svg", {
        "xmlns": NS, "viewBox": f"0 0 {w} {h}",
        "width": str(w), "height": str(h),
    })
    ET.SubElement(svg, "rect", {"width": str(w), "height": str(h), "fill": BG, "rx": "12"})
    return svg


def rect(parent, x, y, w, h, fill=SURFACE, stroke=BORDER, rx=10):
    ET.SubElement(parent, "rect", {
        "x": str(x), "y": str(y), "width": str(w), "height": str(h),
        "fill": fill, "rx": str(rx),
        **({"stroke": stroke, "stroke-width": "1"} if stroke else {}),
    })


def text(parent, x, y, content, *, fill=TEXT, size=10, bold=False, mono=True):
    el = ET.SubElement(parent, "text", {
        "x": str(x), "y": str(y), "fill": fill,
        "font-family": "monospace" if mono else "sans-serif",
        "font-size": str(size), "font-weight": "bold" if bold else "normal",
    })
    el.text = content
    return el


def write(path, svg):
    out = ROOT / path
    out.write_text(ET.tostring(svg, encoding="unicode"))
    print(f"Wrote {path}")


def make_dashboard(user):
    w, h = 900, 200
    svg = svg_open(w, h)
    rect(svg, 8, 8, w - 16, h - 16, fill=SURFACE_2)

    # accent bar
    ET.SubElement(svg, "rect", {"x": "24", "y": "28", "width": "5", "height": "144", "fill": ACCENT_BRIGHT, "rx": "2"})
    ET.SubElement(svg, "rect", {"x": "0", "y": "0", "width": str(w), "height": str(h), "fill": "url(#glow)", "opacity": "0"})

    name = user.get("name") or CONFIG["name"]
    text(svg, 44, 58, name, fill=ACCENT_BRIGHT, size=28, bold=True, mono=False)
    text(svg, 44, 82, CONFIG["tagline"], fill=TEXT, size=12, mono=False)
    text(svg, 44, 102, CONFIG["motto"], fill=MUTED, size=10, mono=False)
    text(svg, 44, 128, f"{CONFIG['location']}  ·  {CONFIG['portfolio'].replace('https://', '')}", fill=MUTED, size=9)

    repos = user["repositories"]["totalCount"]
    stars = sum(r["stargazerCount"] for r in user["repositories"]["nodes"])
    followers = user["followers"]["totalCount"]
    commits = (user.get("contributionsCollection") or {}).get("totalCommitContributions", 0)

    metrics = [("Repos", repos), ("Stars", stars), ("Followers", followers), ("Commits", commits)]
    mx = 500
    for label, val in metrics:
        rect(svg, mx, 36, 88, 56, fill=SURFACE, rx=8)
        text(svg, mx + 12, 58, str(val), fill=ACCENT_BRIGHT, size=18, bold=True)
        text(svg, mx + 12, 76, label.upper(), fill=MUTED, size=8)
        mx += 96

    # focus line
    focus = "  ·  ".join(CONFIG["focus"][:3])
    text(svg, 44, 158, f"Now: {focus}", fill=TEXT, size=9)

    write("dashboard.svg", svg)


def make_heatmap(user):
    cal = (user.get("contributionsCollection") or {}).get("contributionCalendar") or {}
    weeks = cal.get("weeks") or []
    w, h = 900, 130
    svg = svg_open(w, h)
    rect(svg, 8, 8, w - 16, h - 16)

    total = cal.get("totalContributions", 0)
    text(svg, 20, 28, "Contribution activity", fill=ACCENT_BRIGHT, size=11, bold=True)
    text(svg, 200, 28, f"{total} contributions in the last year", fill=MUTED, size=9)

    cell, gap = 11, 3
    ox, oy = 20, 42
    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

    for wi, week in enumerate(weeks[-52:]):
        for di, day in enumerate(week.get("contributionDays", [])):
            count = day.get("contributionCount", 0)
            idx = min(4, count) if count < 5 else 4
            if count >= 10:
                idx = 4
            elif count >= 5:
                idx = 3
            elif count >= 2:
                idx = 2
            elif count >= 1:
                idx = 1
            x = ox + wi * (cell + gap)
            y = oy + di * (cell + gap)
            ET.SubElement(svg, "rect", {
                "x": str(x), "y": str(y), "width": str(cell), "height": str(cell),
                "fill": colors[idx], "rx": "2",
            })

    write("heatmap.svg", svg)


def make_projects(user):
    w, h = 900, 240
    svg = svg_open(w, h)
    rect(svg, 8, 8, w - 16, h - 16)

    text(svg, 20, 30, "Featured projects", fill=ACCENT_BRIGHT, size=12, bold=True)

    repo_map = {r["name"]: r for r in user["repositories"]["nodes"]}
    y = 48
    for item in CONFIG["featured"]:
        name = item["name"]
        repo = repo_map.get(name, {})
        stars = repo.get("stargazerCount", 0)
        rect(svg, 16, y - 4, w - 32, 36, fill=SURFACE, rx=8)
        text(svg, 28, y + 16, name, fill=ACCENT_BRIGHT, size=10, bold=True)
        text(svg, 300, y + 16, item["desc"], fill=MUTED, size=9)
        text(svg, w - 60, y + 16, f"★ {stars}", fill=TEXT, size=9)
        y += 40

    write("projects.svg", svg)


def make_metrics(user):
    repos = user["repositories"]["nodes"]
    w, h = 900, 120
    svg = svg_open(w, h)
    rect(svg, 8, 8, w - 16, h - 16)

    # langs
    langs = {}
    for r in repos:
        pl = r.get("primaryLanguage")
        if pl:
            langs[pl["name"]] = langs.get(pl["name"], 0) + 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:4]

    contrib = user.get("contributionsCollection") or {}
    years = contrib.get("contributionYears") or []

    panels = [
        ("Languages", [f"{n}: {c}" for n, c in top] or ["—"]),
        ("Activity", [
            f"Commits: {contrib.get('totalCommitContributions', 0)}",
            f"Years: {len(years)}",
            f"Following: {user['following']['totalCount']}",
        ]),
        ("Stack", CONFIG["stack"][:4]),
    ]

    px = 20
    for title, lines in panels:
        rect(svg, px, 24, 270, 80, fill=SURFACE, rx=8)
        text(svg, px + 12, 44, title, fill=ACCENT_BRIGHT, size=10, bold=True)
        ty = 60
        for line in lines:
            text(svg, px + 12, ty, line, fill=TEXT, size=9)
            ty += 14
        px += 290

    write("metrics.svg", svg)


def make_toolbar():
    w, h = 900, 88
    svg = svg_open(w, h)
    rect(svg, 8, 8, w - 16, h - 16)

    text(svg, 20, 30, "Stack", fill=ACCENT_BRIGHT, size=10, bold=True)
    x = 20
    for tech in CONFIG["stack"]:
        bw = len(tech) * 7 + 22
        rect(svg, x, 40, bw, 28, fill=SURFACE, rx=6)
        text(svg, x + 11, 58, tech, fill=TEXT, size=9)
        x += bw + 8

    text(svg, 20, 78, "Links: " + "  ·  ".join(l["label"] for l in CONFIG["links"]), fill=MUTED, size=8)

    write("toolbar.svg", svg)


def make_signature():
    w, h = 900, 36
    svg = svg_open(w, h)
    text(svg, 20, 22, "Self-hosted SVGs · regenerated daily · axe01010/profile.config.json", fill=MUTED, size=8)
    write("signature.svg", svg)


if __name__ == "__main__":
    user = fetch_user()
    make_dashboard(user)
    make_heatmap(user)
    make_projects(user)
    make_metrics(user)
    make_toolbar()
    make_signature()

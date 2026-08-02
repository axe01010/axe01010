#!/usr/bin/env python3
"""Generate stats SVG from GitHub GraphQL API."""

import os, json, base64, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

import requests

USERNAME = os.environ.get("USERNAME", "axe01010")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

QUERY = """
query($login:String!){
  user(login:$login){
    login
    name
    bio
    location
    blog
    twitterUsername
    createdAt
    followers{totalCount}
    following{totalCount}
    repositories(ownerAffiliations:OWNER,first:100){
      totalCount
      nodes{
        name
        stargazerCount
        forkCount
        primaryLanguage{name color}
      }
    }
    contributionsCollection{
      contributionYears
      totalCommitContributions
      restrictedContributionsCount
    }
  }
}
"""


def fetch_graphql():
    headers = {"Authorization": f"bearer {TOKEN}"} if TOKEN else {}
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["data"]["user"]


def make_stats_svg(user, repos, output="stats.svg"):
    stars = sum(r["stargazerCount"] for r in repos)
    forks = sum(r["forkCount"] for r in repos)
    followers = user["followers"]["totalCount"]
    following = user["following"]["totalCount"]
    repo_count = user["repositories"]["totalCount"]

    lines = [
        f'<tspan x="10" dy="1.2em">Repos: {repo_count}</tspan>',
        f'<tspan x="10" dy="1.2em">Stars: {stars}</tspan>',
        f'<tspan x="10" dy="1.2em">Forks: {forks}</tspan>',
        f'<tspan x="10" dy="1.2em">Followers: {followers}</tspan>',
        f'<tspan x="10" dy="1.2em">Following: {following}</tspan>',
    ]
    _write_svg(output, "Stats", lines, width=220, height=140)


def make_langs_svg(repos, output="langs.svg"):
    langs = {}
    for r in repos:
        pl = r.get("primaryLanguage")
        if pl:
            name = pl["name"]
            langs[name] = langs.get(name, 0) + 1
    top = sorted(langs.items(), key=lambda x: -x[1])[:6]
    lines = [f'<tspan x="10" dy="1.2em">{n}: {c} repos</tspan>' for n, c in top]
    _write_svg(output, "Top Languages", lines, width=220, height=120)


def make_streak_svg(user, output="streak.svg"):
    contrib = user.get("contributionsCollection") or {}
    years = contrib.get("contributionYears") or []
    current = years[-1] if years else datetime.now().year
    total = contrib.get("totalCommitContributions", 0)
    lines = [
        f'<tspan x="10" dy="1.2em">Year: {current}</tspan>',
        f'<tspan x="10" dy="1.2em">Commits: {total}</tspan>',
        f'<tspan x="10" dy="1.2em">Active: {len(years)} yrs</tspan>',
    ]
    _write_svg(output, "Streak", lines, width=220, height=120)


def make_year_svg(user, output="year.svg"):
    contrib = user.get("contributionsCollection") or {}
    years = contrib.get("contributionYears") or []
    lines = [
        f'<tspan x="10" dy="1.2em">{y}</tspan>'
        for y in (years[-10:] or [datetime.now().year])
    ]
    _write_svg(output, "Years", lines, width=220, height=120)


def _write_svg(path, title, lines, width=220, height=120):
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    svg = ET.Element(
        "svg",
        {
            "xmlns": ns,
            "viewBox": f"0 0 {width} {height}",
            "width": str(width),
            "height": str(height),
        },
    )
    ET.SubElement(
        svg,
        "rect",
        {"width": str(width), "height": str(height), "fill": "#0f0f23", "rx": "8"},
    )
    ET.SubElement(
        svg,
        "text",
        {
            "x": "10",
            "y": "18",
            "fill": "#8b949e",
            "font-family": "monospace",
            "font-size": "10",
            "font-weight": "bold",
        },
    ).text = title
    tspans = "\n".join(lines)
    ET.SubElement(
        svg,
        "text",
        {
            "x": "10",
            "y": "35",
            "fill": "#c9d1d9",
            "font-family": "monospace",
            "font-size": "9",
        },
    ).text = ""
    # Append tspans manually
    text_el = svg.findall(".//{http://www.w3.org/2000/svg}text")[-1]
    for line in lines:
        t = ET.SubElement(
            text_el, "{http://www.w3.org/2000/svg}tspan", {"x": "10", "dy": "1.2em"}
        )
        t.text = line.split(">")[1].split("<")[0] if "<tspan" in line else line
    Path(path).write_text(ET.tostring(svg, encoding="unicode"))
    print(f"Wrote {path}")


def make_hd_svg(text, path, width=220, height=40):
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    svg = ET.Element(
        "svg",
        {
            "xmlns": ns,
            "viewBox": f"0 0 {width} {height}",
            "width": str(width),
            "height": str(height),
        },
    )
    ET.SubElement(
        svg,
        "rect",
        {"width": str(width), "height": str(height), "fill": "#0f0f23", "rx": "6"},
    )
    ET.SubElement(
        svg,
        "text",
        {
            "x": "10",
            "y": "26",
            "fill": "#c9d1d9",
            "font-family": "monospace",
            "font-size": "11",
            "font-weight": "bold",
        },
    ).text = text
    Path(path).write_text(ET.tostring(svg, encoding="unicode"))
    print(f"Wrote {path}")


if __name__ == "__main__":
    user = fetch_graphql()
    repos = user["repositories"]["nodes"]
    make_stats_svg(user, repos, "stats.svg")
    make_langs_svg(repos, "langs.svg")
    make_streak_svg(user, "streak.svg")
    make_year_svg(user, "year.svg")
    make_hd_svg("About", "hd-about.svg", width=120, height=30)
    make_hd_svg("Stack", "hd-stack.svg", width=80, height=30)
    make_hd_svg("Projects", "hd-projects.svg", width=100, height=30)
    make_hd_svg("Stats", "hd-stats.svg", width=70, height=30)
    make_hd_svg("About this page", "hd-about-this-page.svg", width=160, height=30)

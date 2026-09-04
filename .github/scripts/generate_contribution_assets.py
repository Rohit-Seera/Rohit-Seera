#!/usr/bin/env python3
"""Generate local GitHub profile cards and scale the contribution snake."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
PROFILE = ROOT / "profile"
DATA = ROOT / "contributions.json"

payload = json.loads(DATA.read_text(encoding="utf-8"))
try:
    collection = payload["data"]["user"]["contributionsCollection"]
    total = int(collection["contributionCalendar"]["totalContributions"])
    commits = int(collection["totalCommitContributions"])
except (KeyError, TypeError, ValueError) as exc:
    raise SystemExit(f"Could not read contribution data: {exc}")

public_repos = int(os.environ.get("PUBLIC_REPOS", "0"))

DIST.mkdir(parents=True, exist_ok=True)
PROFILE.mkdir(parents=True, exist_ok=True)

# Keep the snake visually usable while allowing it to grow as contribution volume grows.
scale = min(1.35, 1.0 + total / 1800.0)


def scale_svg(path: Path) -> None:
    if not path.exists():
        return
    svg = path.read_text(encoding="utf-8")
    match = re.search(r"<svg\b([^>]*)>", svg, flags=re.I)
    if not match:
        return
    attrs = match.group(1)
    width_m = re.search(r'\bwidth="([^"]+)"', attrs)
    height_m = re.search(r'\bheight="([^"]+)"', attrs)
    if not (width_m and height_m):
        return

    def numeric(value: str) -> float:
        found = re.match(r"([0-9.]+)", value)
        return float(found.group(1)) if found else 1000.0

    width = numeric(width_m.group(1))
    height = numeric(height_m.group(1))
    attrs = re.sub(r'\bwidth="[^"]+"', f'width="{round(width * scale)}"', attrs, count=1)
    attrs = re.sub(r'\bheight="[^"]+"', f'height="{round(height * scale)}"', attrs, count=1)
    path.write_text(svg[:match.start(1)] + attrs + svg[match.end(1):], encoding="utf-8")


for name in ("github-snake.svg", "github-snake-dark.svg"):
    scale_svg(DIST / name)

stats = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="220" viewBox="0 0 900 220">
<rect width="900" height="220" rx="18" fill="#0D1117"/>
<text x="450" y="48" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="27" font-weight="700" fill="#A78BFA">GitHub Stats</text>
<text x="300" y="112" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="34" font-weight="800" fill="#78FF9C">{total:,}</text>
<text x="300" y="143" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="17" fill="#C9D1D9">Total Contributions</text>
<text x="600" y="112" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="34" font-weight="800" fill="#78FF9C">{commits:,}</text>
<text x="600" y="143" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="17" fill="#C9D1D9">Total Commits</text>
<text x="450" y="192" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="#8B949E">Public repos: {public_repos:,} · Auto-refreshed by GitHub Actions</text>
</svg>
'''
(PROFILE / "stats.svg").write_text(stats, encoding="utf-8")

count = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="100" viewBox="0 0 1000 100">
<rect width="1000" height="100" rx="16" fill="#0D1117"/>
<text x="500" y="62" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="31" font-weight="700" fill="#C9D1D9">Total GitHub contributions: <tspan fill="#78FF9C">{total:,}</tspan></text>
</svg>
'''
(PROFILE / "contribution-count.svg").write_text(count, encoding="utf-8")

# The snake walks the same contribution calendar shown in the heat map.
# This live card therefore reports the cumulative contributions represented by the snake.
eaten = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="140" viewBox="0 0 1000 140">
<rect width="1000" height="140" rx="18" fill="#0D1117"/>
<text x="500" y="51" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="25" font-weight="700" fill="#A78BFA">🐍 Contributions Eaten by Snake</text>
<text x="500" y="101" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="38" font-weight="800" fill="#78FF9C">{total:,}</text>
</svg>
'''
(PROFILE / "contribution-eaten.svg").write_text(eaten, encoding="utf-8")

(DIST / "contribution-count.svg").write_text(count, encoding="utf-8")
(DIST / "contribution-eaten.svg").write_text(eaten, encoding="utf-8")

print(f"Total contributions: {total}")
print(f"Total commits: {commits}")
print(f"Public repos: {public_repos}")
print(f"Snake scale: {scale:.3f}x")

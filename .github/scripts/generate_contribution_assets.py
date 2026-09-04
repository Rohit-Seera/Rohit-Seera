#!/usr/bin/env python3
"""Generate contribution count + scale the snake assets from the yearly total."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
DATA = ROOT / "contributions.json"

payload = json.loads(DATA.read_text(encoding="utf-8"))
try:
    total = int(
        payload["data"]["user"]["contributionsCollection"]
        ["contributionCalendar"]["totalContributions"]
    )
except (KeyError, TypeError, ValueError) as exc:
    raise SystemExit(f"Could not read totalContributions: {exc}")

DIST.mkdir(parents=True, exist_ok=True)

# The snake grows gradually as the total contribution count grows.
# Cap the scale so it stays visually usable on the profile.
scale = min(1.35, 1.0 + total / 1800.0)


def scale_svg(path: Path) -> None:
    if not path.exists():
        return
    svg = path.read_text(encoding="utf-8")
    m = re.search(r'<svg\b([^>]*)>', svg, flags=re.I)
    if not m:
        return

    attrs = m.group(1)
    width_m = re.search(r'\bwidth="([^"]+)"', attrs)
    height_m = re.search(r'\bheight="([^"]+)"', attrs)
    if not (width_m and height_m):
        return

    def numeric(value: str) -> float:
        match = re.match(r'([0-9.]+)', value)
        return float(match.group(1)) if match else 1000.0

    width = numeric(width_m.group(1))
    height = numeric(height_m.group(1))
    new_width = round(width * scale)
    new_height = round(height * scale)

    attrs = re.sub(r'\bwidth="[^"]+"', f'width="{new_width}"', attrs, count=1)
    attrs = re.sub(r'\bheight="[^"]+"', f'height="{new_height}"', attrs, count=1)
    svg = svg[:m.start(1)] + attrs + svg[m.end(1):]
    path.write_text(svg, encoding="utf-8")


for name in ("github-snake.svg", "github-snake-dark.svg"):
    scale_svg(DIST / name)

banner = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="120" viewBox="0 0 1000 120">
<rect width="1000" height="120" rx="18" fill="#0D1117"/>
<text x="500" y="46" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"
      font-size="24" font-weight="700" fill="#A78BFA">🐍 Contributions Eaten by Snake</text>
<text x="500" y="88" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"
      font-size="36" font-weight="800" fill="#78FF9C">{total:,}</text>
</svg>
"""
(DIST / "contribution-eaten.svg").write_text(banner, encoding="utf-8")

count = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="90" viewBox="0 0 1000 90">
<rect width="1000" height="90" rx="16" fill="#0D1117"/>
<text x="500" y="56" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"
      font-size="30" font-weight="700" fill="#C9D1D9">Total GitHub contributions: <tspan fill="#78FF9C">{total:,}</tspan></text>
</svg>
"""
(DIST / "contribution-count.svg").write_text(count, encoding="utf-8")

print(f"Total contributions: {total}")
print(f"Snake scale: {scale:.3f}x")

#!/usr/bin/env python3
"""
generate_chart.py
Fetches GitHub traffic data for all public repos, updates the
"Most Visited" section in README.md, and generates assets/traffic-chart.svg.
"""

import os
import re
import subprocess
from datetime import datetime, timezone
import requests

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USERNAME = "mariofahmi"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

REPO_LABELS = {
    "bogaseri": "🎲 BOGA SERI",
    "Ular-Tangga-PIS": "🐍🪜 Ular Tangga PIS",
    "SIAPA-INGIN-MENJADI-KAISAR-IPS": "👑 Siapa Ingin Menjadi Kaisar IPS",
    "Simulasi-Peradilan-Semu-PPKn-": "⚖️ Peradilan Semu",
    "Siapa-yang-Ingin-Menjadi-Mahaguru": "🎓 Siapa yang Ingin Menjadi Mahaguru",
    "PyDuel-Battle-of-Algorithms": "🐍 PyDuel: Battle of Algorithms",
    "CivicQUEST": "🏛️ CivicQUEST",
    "Pahlawan-Cilik-Siaga-Lingkungan": "🌱🦸 Pahlawan Cilik Siaga Lingkungan",
    "webgis-pesisir-tuban": "🛰️ WebGIS Pesisir Tuban",
    "Titen-Laku-Jawa": "🗓️ Titen Laku Jawa",
    "Metode-Penelitian-Sosial": "🔬 Metode Penelitian Sosial",
}

REPO_DESCRIPTIONS = {
    "bogaseri": "An interactive web-based board game teaching Indonesian traffic safety.",
    "Ular-Tangga-PIS": "An educational Snakes &amp; Ladders game for Introduction to Social Sciences.",
    "SIAPA-INGIN-MENJADI-KAISAR-IPS": 'A "Who Wants to Be a Millionaire"-style quiz game on Social Studies (IPS).',
    "Simulasi-Peradilan-Semu-PPKn-": "An interactive moot court simulation for PPKn UNIROW Tuban students.",
    "Siapa-yang-Ingin-Menjadi-Mahaguru": "An educational quiz game exploring the history of teachers and the AI revolution.",
    "PyDuel-Battle-of-Algorithms": "An educational Python and algorithms game — speed-duel against PyBot AI.",
    "CivicQUEST": "A PPKn education game featuring Survival Quiz, RPG Ethics Dilemma, and Boss Battle.",
    "Pahlawan-Cilik-Siaga-Lingkungan": "An educational gamification web app for children&#39;s 3R awareness and waste management.",
    "webgis-pesisir-tuban": "An interactive coastal mapping portal with Leaflet &amp; Gemini AI Assistant.",
    "Titen-Laku-Jawa": "A precise application for calculating traditional Javanese time cycles.",
    "Metode-Penelitian-Sosial": "An interactive platform that guides students and researchers in understanding social research paradigms, preventing methodological bias, and drafting research methods with ease.",
}

REPO_URLS = {
    r: f"https://mariofahmi.github.io/{r}/" for r in REPO_LABELS
}

def get_traffic(repo):
    url = f"https://api.github.com/repos/{USERNAME}/{repo}/traffic/views"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return data.get("count", 0), data.get("uniques", 0)
    except Exception as e:
        print(f"Error fetching {repo}: {e}")
    return 0, 0

def generate_svg(top_repos, total_all_views):
    W = 760
    H = 220
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    bars_svg = ""
    start_y = 60
    row_height = 42
    max_views = max([r[0] for r in top_repos] + [1])
    bar_max_width = 380

    for i, (views, uniques, repo) in enumerate(top_repos[:3]):
        y = start_y + i * row_height
        bar_w = max(10, int((views / max_views) * bar_max_width))
        label = REPO_LABELS.get(repo, repo)
        medals = ["🥇", "🥈", "🥉"]
        medal = medals[i] if i < len(medals) else "•"

        bars_svg += f'''
    <!-- Row {i+1} -->
    <text x="35" y="{y + 16}" fill="#e2e8f0" font-size="13" font-family="system-ui, -apple-system, sans-serif">{medal} {label}</text>
    <rect x="230" y="{y + 4}" width="{bar_w}" height="18" rx="9" fill="url(#barGrad{i})"/>
    <text x="{230 + bar_w + 12}" y="{y + 17}" fill="#94a3b8" font-size="12" font-family="monospace" font-weight="bold">{views} views ({uniques} unique)</text>
'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="50%" stop-color="#1e1b4b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="barGrad0" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#fbbf24"/>
    </linearGradient>
    <linearGradient id="barGrad1" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#94a3b8"/>
      <stop offset="100%" stop-color="#cbd5e1"/>
    </linearGradient>
    <linearGradient id="barGrad2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
  </defs>

  <!-- Card Background -->
  <rect width="{W}" height="{H}" rx="14" fill="url(#bgGrad)"/>
  <rect width="{W}" height="{H}" rx="14" fill="none" stroke="#334155" stroke-width="1.5"/>

  <!-- Header -->
  <text x="35" y="34" fill="#38bdf8" font-size="14" font-family="system-ui, -apple-system, sans-serif" font-weight="bold">🔥 Most Popular Projects (Last 14 Days)</text>
  <text x="{W - 35}" y="34" fill="#64748b" font-size="11" font-family="monospace" text-anchor="end">Total: {total_all_views} views · Updated: {now}</text>

  <line x1="35" y1="44" x2="{W - 35}" y2="44" stroke="#334155" stroke-width="1"/>

  <!-- Bars -->
  {bars_svg}

  <!-- Footer Info -->
  <text x="35" y="{H - 16}" fill="#64748b" font-size="10" font-family="system-ui, -apple-system, sans-serif">⚡ Automatically updated daily via GitHub Actions</text>
</svg>'''

    os.makedirs("assets", exist_ok=True)
    with open("assets/traffic-chart.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("assets/traffic-chart.svg generated successfully.")

def update_readme(top3):
    medals = ["🥇", "🥈", "🥉"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    rows = ""
    for i, (views, uniques, repo) in enumerate(top3):
        label = REPO_LABELS[repo]
        desc = REPO_DESCRIPTIONS.get(repo, "")
        url = REPO_URLS[repo]
        medal = medals[i]
        rows += f"""    <tr>
      <td align="center">{medal}</td>
      <td><a href="{url}"><b>{label}</b></a></td>
      <td>{desc}</td>
      <td align="center"><nobr>{views} views</nobr></td>
    </tr>
"""

    new_section = f"""### 🔥 Most Visited (Last 14 Days)

<table>
  <thead>
    <tr>
      <th width="5%" align="center">Rank</th>
      <th width="28%" align="left">Project</th>
      <th width="53%" align="left">Description</th>
      <th width="14%" align="center">Views</th>
    </tr>
  </thead>
  <tbody>
{rows}  </tbody>
</table>

> 📊 *Last updated: {today} UTC — Traffic data reflects the last 14 days via GitHub Insights.*"""

    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            readme = f.read()

        pattern = r"(### 🔥 Most Visited.*?)(?=\n---\n)"
        new_readme = re.sub(pattern, new_section, readme, flags=re.DOTALL)

        if new_readme != readme:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_readme)
            print("README.md updated successfully.")
        else:
            print("README.md content unchanged or pattern not matched.")

def main():
    print("Fetching traffic data...")
    results = []
    total_views = 0
    for repo in REPO_LABELS:
        views, uniques = get_traffic(repo)
        results.append((views, uniques, repo))
        total_views += views
        print(f"  {repo}: {views} views, {uniques} unique")

    results.sort(reverse=True)
    top3 = results[:3]

    # 1. Update README
    update_readme(top3)

    # 2. Generate SVG
    generate_svg(results, total_views)

    # 3. Git stage & remote setup
    try:
        subprocess.run(["git", "add", "README.md", "assets/traffic-chart.svg"], check=False)
        if TOKEN:
            subprocess.run([
                "git", "remote", "set-url", "origin",
                f"https://x-access-token:{TOKEN}@github.com/{USERNAME}/mariofahmi.git"
            ], check=False)
        print("Git add and remote setup completed.")
    except Exception as e:
        print(f"Git note: {e}")

if __name__ == "__main__":
    main()

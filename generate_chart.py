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
    "NetWorth-Anda": "💰 NetWorth Anda",
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
    "NetWorth-Anda": "A modern, privacy-first personal wealth tracker and financial freedom planner.",
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
        else:
            print(f"  [HTTP {r.status_code}] Unable to fetch {repo}: {r.text[:80]}")
    except Exception as e:
        print(f"Error fetching {repo}: {e}")
    return 0, 0

def generate_svg(top_repos, total_all_views):
    W = 780
    H = 296
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    bars_svg = ""
    start_y = 72
    row_height = 64
    max_views = max([r[0] for r in top_repos] + [1])
    bar_max_width = 692

    medals = ["🥇 #1", "🥈 #2", "🥉 #3"]
    rank_colors = ["#fbbf24", "#38bdf8", "#fb923c"]
    rank_bg_opacities = ["#f59e0b", "#38bdf8", "#f97316"]

    for i, (views, uniques, repo) in enumerate(top_repos[:3]):
        y = start_y + i * row_height
        bar_w = max(18, int((views / max_views) * bar_max_width))
        label = REPO_LABELS.get(repo, repo)
        medal = medals[i] if i < len(medals) else f"#{i+1}"
        col = rank_colors[i] if i < len(rank_colors) else "#94a3b8"
        bg_col = rank_bg_opacities[i] if i < len(rank_bg_opacities) else "#334155"

        bars_svg += f'''
  <!-- Row {i+1}: {label} -->
  <g transform="translate(32, {y})">
    <rect width="716" height="56" rx="10" fill="#0f172a" fill-opacity="0.75" stroke="#334155" stroke-width="0.8"/>
    
    <!-- Rank Pill -->
    <rect x="12" y="10" width="50" height="20" rx="6" fill="{bg_col}" fill-opacity="0.15" stroke="{bg_col}" stroke-opacity="0.5" stroke-width="1"/>
    <text x="37" y="24" fill="{col}" font-size="11" font-weight="bold" font-family="system-ui, sans-serif" text-anchor="middle">{medal}</text>
    
    <!-- Project Title (Generous unobstructed space) -->
    <text x="72" y="24" fill="#f8fafc" font-size="13.5" font-weight="700" font-family="'Plus Jakarta Sans', system-ui, -apple-system, sans-serif">{label}</text>
    
    <!-- Views Metric -->
    <text x="704" y="24" fill="{col}" font-size="12.5" font-weight="bold" font-family="monospace" text-anchor="end">{views} views <tspan fill="#64748b" font-weight="normal" font-size="11">({uniques} unique)</tspan></text>
    
    <!-- Progress Bar (Dedicated bottom tier, immune to text overlap) -->
    <rect x="12" y="38" width="692" height="7" rx="3.5" fill="#1e293b"/>
    <rect x="12" y="38" width="{bar_w}" height="7" rx="3.5" fill="url(#barGrad{i})"/>
  </g>
'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <!-- Deep Glassmorphism Gradient Background -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090d16"/>
      <stop offset="40%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#0b1120"/>
    </linearGradient>

    <!-- Card Border Aurora Gradient -->
    <linearGradient id="borderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.6"/>
      <stop offset="50%" stop-color="#818cf8" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#334155" stop-opacity="0.6"/>
    </linearGradient>

    <!-- Title Aurora Gradient -->
    <linearGradient id="titleGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>

    <!-- Rank 1 Gold Flame Gradient -->
    <linearGradient id="barGrad0" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f59e0b"/>
      <stop offset="50%" stop-color="#fbbf24"/>
      <stop offset="100%" stop-color="#fde047"/>
    </linearGradient>

    <!-- Rank 2 Cyber Cyan Gradient -->
    <linearGradient id="barGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284c7"/>
      <stop offset="50%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#93c5fd"/>
    </linearGradient>

    <!-- Rank 3 Radiant Sunset Gradient -->
    <linearGradient id="barGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ea580c"/>
      <stop offset="50%" stop-color="#f97316"/>
      <stop offset="100%" stop-color="#fdba74"/>
    </linearGradient>

    <!-- Subtle Drop Shadow Filter -->
    <filter id="shadowFilter" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
  </defs>

  <!-- Main Background Container -->
  <rect width="{W}" height="{H}" rx="16" fill="url(#bgGrad)" filter="url(#shadowFilter)"/>
  <rect width="{W}" height="{H}" rx="16" fill="none" stroke="url(#borderGrad)" stroke-width="1.2"/>

  <!-- Ambient Glow Effect in Top Right -->
  <circle cx="720" cy="40" r="90" fill="#38bdf8" fill-opacity="0.05" filter="blur(20px)"/>

  <!-- ==================== HEADER ==================== -->
  <g transform="translate(32, 22)">
    <!-- Fire Icon with Glow -->
    <rect x="0" y="0" width="30" height="30" rx="8" fill="#f59e0b" fill-opacity="0.15" stroke="#f59e0b" stroke-opacity="0.3" stroke-width="1"/>
    <text x="15" y="21" font-size="15" text-anchor="middle">🔥</text>

    <!-- Header Titles -->
    <text x="38" y="16" fill="url(#titleGrad)" font-size="15" font-weight="800" font-family="'Plus Jakarta Sans', system-ui, -apple-system, sans-serif" letter-spacing="0.3px">Most Popular Projects</text>
    <text x="38" y="29" fill="#64748b" font-size="11" font-family="system-ui, -apple-system, sans-serif">Last 14 Days Activity · High Traffic Ranking</text>

    <!-- Right Header Pill -->
    <rect x="510" y="2" width="206" height="26" rx="13" fill="#1e293b" fill-opacity="0.7" stroke="#334155" stroke-width="0.8"/>
    <text x="613" y="19" fill="#94a3b8" font-size="11" font-family="monospace" font-weight="600" text-anchor="middle">
      <tspan fill="#38bdf8" font-weight="bold">{total_all_views}</tspan> views · {now}
    </text>
  </g>

  <!-- Header Divider -->
  <line x1="32" y1="62" x2="748" y2="62" stroke="#1e293b" stroke-width="1"/>

  <!-- Leaderboard Rows -->
  {bars_svg}

  <!-- ==================== FOOTER ==================== -->
  <line x1="32" y1="264" x2="748" y2="264" stroke="#1e293b" stroke-width="0.8"/>

  <!-- Live Green Pulsing Indicator -->
  <circle cx="44" cy="279" r="4" fill="#22c55e"/>
  <circle cx="44" cy="279" r="7" fill="none" stroke="#22c55e" stroke-width="1.5">
    <animate attributeName="r" values="4;9" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0" dur="2s" repeatCount="indefinite"/>
  </circle>

  <text x="58" y="283" fill="#64748b" font-size="11" font-family="system-ui, -apple-system, sans-serif">Auto-synced daily via GitHub Actions</text>
  <text x="748" y="283" fill="#475569" font-size="10.5" font-family="system-ui, -apple-system, sans-serif" text-anchor="end">UNIROW Tuban · Mario Fahmi</text>
</svg>'''

    os.makedirs("assets", exist_ok=True)
    with open("assets/traffic-chart.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("assets/traffic-chart.svg generated successfully.")

def update_readme(top3):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    new_section = f"""### 🔥 Most Visited (Last 14 Days)

<p align="center">
  <img src="https://raw.githubusercontent.com/mariofahmi/mariofahmi/main/assets/traffic-chart.svg?v={today}" alt="Most Popular Projects Traffic Chart" />
</p>"""

    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            readme = f.read()

        pattern = r"(### 🔥 Most Visited.*?)(?=\r?\n---)"
        new_readme = re.sub(pattern, new_section, readme, flags=re.DOTALL)

        if new_readme != readme:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(new_readme)
            print("README.md updated successfully.")
        else:
            print("README.md content unchanged or pattern not matched.")

def main():
    try:
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

        if total_views == 0 and os.path.exists("assets/traffic-chart.svg"):
            print("⚠️ Warning: Total views is 0. Token might be missing or API rate-limited. Preserving existing chart.")
            return

        # 1. Update README
        update_readme(top3)

        # 2. Generate SVG
        generate_svg(results, total_views)

        # 3. Stage changes safely
        try:
            subprocess.run(["git", "add", "README.md", "assets/traffic-chart.svg"], check=False)
            print("Git stage completed successfully.")
        except Exception as e:
            print(f"Git stage note: {e}")

    except Exception as e:
        print(f"Handled exception in main: {e}")
        # Exit gracefully without throwing unhandled error to prevent GitHub failure emails

if __name__ == "__main__":
    main()

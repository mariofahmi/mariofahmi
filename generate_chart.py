#!/usr/bin/env python3
"""
generate_chart.py
Fetches GitHub traffic data for all public repos and updates the
"Most Visited" section in README.md automatically.
"""

import os
import re
import requests
from datetime import datetime

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
    "SIAPA-INGIN-MENJADI-KAISAR-IPS": "A \"Who Wants to Be a Millionaire\"-style quiz game on Social Studies (IPS).",
    "Simulasi-Peradilan-Semu-PPKn-": "An interactive moot court simulation for PPKn UNIROW Tuban students.",
    "Siapa-yang-Ingin-Menjadi-Mahaguru": "An educational quiz game exploring the history of teachers and the AI revolution.",
    "PyDuel-Battle-of-Algorithms": "An educational Python and algorithms game — speed-duel against PyBot AI.",
    "CivicQUEST": "A PPKn education game featuring Survival Quiz, RPG Ethics Dilemma, and Boss Battle.",
    "Pahlawan-Cilik-Siaga-Lingkungan": "An educational gamification web app for children&#39;s 3R awareness and waste management.",
    "webgis-pesisir-tuban": "An interactive coastal mapping portal with Leaflet &amp; Gemini AI Assistant.",
    "Titen-Laku-Jawa": "A precise application for calculating traditional Javanese time cycles.",
    "Metode-Penelitian-Sosial": "An interactive platform for understanding social research paradigms and preventing methodological bias.",
}

REPO_URLS = {
    r: f"https://mariofahmi.github.io/{r}/" for r in REPO_LABELS
}

def get_traffic(repo):
    url = f"https://api.github.com/repos/{USERNAME}/{repo}/traffic/views"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        return data.get("count", 0), data.get("uniques", 0)
    return 0, 0

def main():
    print("Fetching traffic data...")
    results = []
    for repo in REPO_LABELS:
        views, uniques = get_traffic(repo)
        results.append((views, uniques, repo))
        print(f"  {repo}: {views} views, {uniques} unique")

    results.sort(reverse=True)
    top3 = results[:3]

    medals = ["🥇", "🥈", "🥉"]
    today = datetime.utcnow().strftime("%Y-%m-%d")

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

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    # Replace section between ### 🔥 Most Visited ... and next ---
    pattern = r"(### 🔥 Most Visited.*?)(?=\n---\n)"
    new_readme = re.sub(pattern, new_section, readme, flags=re.DOTALL)

    if new_readme == readme:
        print("WARNING: Pattern not found, appending not done.")
    else:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme)
        print("README.md updated successfully.")

if __name__ == "__main__":
    main()
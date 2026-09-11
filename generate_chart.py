import os
import requests
from datetime import datetime, timezone

USERNAME = "mariofahmi"
REPO = "mariofahmi"
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def fetch_traffic():
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/traffic/views"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    return r.json().get("views", [])

def generate_svg(views):
    if not views:
        views = []

    # Take last 14 days
    views = views[-14:]
    labels = [v["timestamp"][:10] for v in views]
    counts = [v["count"] for v in views]
    uniques = [v["uniques"] for v in views]

    max_val = max(counts + [1])
    n = len(labels)

    W = 760
    H = 220
    pad_left = 45
    pad_right = 20
    pad_top = 30
    pad_bottom = 55
    chart_w = W - pad_left - pad_right
    chart_h = H - pad_top - pad_bottom
    bar_gap = 6
    bar_w = max(6, (chart_w / max(n, 1)) - bar_gap)

    # Y grid lines
    grid_lines = ""
    y_ticks = 4
    for i in range(y_ticks + 1):
        y_val = int(max_val * i / y_ticks)
        y_pos = pad_top + chart_h - (chart_h * i / y_ticks)
        grid_lines += f'<line x1="{pad_left}" y1="{y_pos:.1f}" x2="{W - pad_right}" y2="{y_pos:.1f}" stroke="#333" stroke-width="1" stroke-dasharray="4,4"/>'
        grid_lines += f'<text x="{pad_left - 6}" y="{y_pos + 4:.1f}" fill="#888" font-size="10" text-anchor="end">{y_val}</text>'

    # Bars
    bars = ""
    x_labels = ""
    total_views = sum(counts)
    total_uniques = sum(uniques)

    for i, (label, count, unique) in enumerate(zip(labels, counts, uniques)):
        x = pad_left + i * (bar_w + bar_gap)
        bar_h = (count / max_val) * chart_h if max_val > 0 else 0
        y = pad_top + chart_h - bar_h

        # Gradient effect via opacity
        bars += f'''<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" 
            rx="3" fill="url(#barGrad)" opacity="0.9"/>'''
        # Unique visitors dot
        if unique > 0:
            uy = pad_top + chart_h - (unique / max_val) * chart_h
            bars += f'<circle cx="{x + bar_w/2:.1f}" cy="{uy:.1f}" r="3" fill="#ff6b9d"/>'

        # Count label on top of bar
        if count > 0:
            bars += f'<text x="{x + bar_w/2:.1f}" y="{y - 4:.1f}" fill="#e2e8f0" font-size="9" text-anchor="middle">{count}</text>'

        # X label (show every 2nd if many bars)
        short_label = label[5:]  # MM-DD
        if n <= 7 or i % 2 == 0:
            x_labels += f'<text x="{x + bar_w/2:.1f}" y="{H - 8}" fill="#888" font-size="9" text-anchor="middle" transform="rotate(-30, {x + bar_w/2:.1f}, {H - 8})">{short_label}</text>'

    # Updated time
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1a1a2e"/>
      <stop offset="100%" stop-color="#16213e"/>
    </linearGradient>
    <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#ff6b9d"/>
      <stop offset="100%" stop-color="#c44569"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="{W}" height="{H}" rx="12" fill="url(#bgGrad)"/>
  <rect width="{W}" height="{H}" rx="12" fill="none" stroke="#333" stroke-width="1"/>

  <!-- Title -->
  <text x="16" y="20" fill="#ff6b9d" font-size="12" font-family="monospace" font-weight="bold">📊 Profile Views — Last 14 Days</text>
  <text x="{W - pad_right}" y="20" fill="#555" font-size="10" font-family="monospace" text-anchor="end">Updated: {now}</text>

  <!-- Grid -->
  {grid_lines}

  <!-- Bars -->
  {bars}

  <!-- X labels -->
  {x_labels}

  <!-- Legend -->
  <rect x="{pad_left}" y="{H - 18}" width="10" height="8" rx="2" fill="url(#barGrad)"/>
  <text x="{pad_left + 14}" y="{H - 11}" fill="#aaa" font-size="10" font-family="monospace">Views ({total_views} total)</text>
  <circle cx="{pad_left + 120}" cy="{H - 14}" r="4" fill="#ff6b9d"/>
  <text x="{pad_left + 128}" y="{H - 11}" fill="#aaa" font-size="10" font-family="monospace">Unique ({total_uniques} total)</text>
</svg>'''

    os.makedirs("assets", exist_ok=True)
    with open("assets/traffic-chart.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Chart generated: {len(views)} days, {total_views} total views, {total_uniques} unique")

if __name__ == "__main__":
    print("Fetching GitHub traffic data...")
    views = fetch_traffic()
    print(f"Got {len(views)} data points")
    generate_svg(views)
    print("Done!")

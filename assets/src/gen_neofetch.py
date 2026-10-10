#!/usr/bin/env python3
"""Neofetch-style profile card: colour ASCII portrait + GitHub stats.

Replaces the hero/boot banners. Reads assets/src/portrait.ppm (a pre-cropped
P3 image) and assets/src/stats.json (written by fetch_stats.py).
"""
import json
import math
from datetime import date, timedelta

W = 1200
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

BG, PANE = "#04060b", "#070d16"
FRAME, MUTED = "#16405e", "#5b768c"
CYAN, WHITE = "#22d3ee", "#e6edf3"

RAMP = " .:-=+*#%@"

PORT_X = 40
INFO_X = 480
ROW_STEP = 14
INFO_STEP = 18
FONT = 12
TOP = 40
PAD = 40

PORTRAIT_ROWS = 30


def _luma(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def ascii_portrait(path="assets/src/portrait.ppm"):
    with open(path) as fh:
        tokens = fh.read().split()
    if tokens[0] != "P3":
        raise ValueError(f"{path}: not a P3 PPM")
    w, h = int(tokens[1]), int(tokens[2])
    vals = list(map(int, tokens[4:4 + w * h * 3]))
    rows = []
    i = 0
    for _ in range(h):
        row = []
        for _ in range(w):
            r, g, b = vals[i], vals[i + 1], vals[i + 2]
            i += 3
            l = _luma(r, g, b)
            mx, mn = max(r, g, b), min(r, g, b)
            sat = 0.0 if mx == 0 else (mx - mn) / mx
            if l > 200 and sat < 0.18:
                row.append((" ", None))
                continue
            ch = RAMP[max(1, int(l / 256 * 10))]
            if l < 70:
                # Plan's lift is multiply by 70/l; that cannot reach luma 70 for
                # black (0*l stays 0) or for saturated pixels whose bright channel
                # clamps at 255. Fall back to a white blend only for those.
                if l > 0:
                    factor = 70.0 / l
                    r = min(255.0, r * factor)
                    g = min(255.0, g * factor)
                    b = min(255.0, b * factor)
                nl = _luma(r, g, b)
                if nl < 70:
                    t = (70.0 - nl) / (255.0 - nl)
                    r, g, b = r + (255 - r) * t, g + (255 - g) * t, b + (255 - b) * t
                r, g, b = math.ceil(r), math.ceil(g), math.ceil(b)
            row.append((ch, "#%02x%02x%02x" % (r, g, b)))
        rows.append(row)
    return rows


def uptime(since, today):
    if isinstance(since, str):
        since = date.fromisoformat(since)
    years = today.year - since.year
    months = today.month - since.month
    days = today.day - since.day
    if days < 0:
        months -= 1
        days += (today.replace(day=1) - timedelta(days=1)).day
    if months < 0:
        years -= 1
        months += 12
    return (
        f"{years} year" + ("" if years == 1 else "s") + ", "
        f"{months} month" + ("" if months == 1 else "s") + ", "
        f"{days} day" + ("" if days == 1 else "s")
    )


def _info_lines(stats, today):
    return [
        [("sharvin@streamwave", CYAN, 700)],
        [("------------------", MUTED)],
        [("OS: ", CYAN), ("........... ", MUTED), ("macOS, Debian 13, Unraid", WHITE)],
        [("Uptime: ", CYAN), ("....... ", MUTED), (uptime("2020-11-11", today), WHITE)],
        [("Host: ", CYAN), ("......... ", MUTED), ("Streamwave home lab · OCI edge", WHITE)],
        [("Kernel: ", CYAN), ("....... ", MUTED), ("AI Systems Engineer", WHITE)],
        [("IDE: ", CYAN), (".......... ", MUTED), ("Claude Code, VS Code", WHITE)],
        [],
        [("Languages.Programming: ", CYAN), ("Go, Python, TypeScript, Rust, Kotlin", WHITE)],
        [("Languages.Real: ", CYAN), ("....... ", MUTED), ("English, Malayalam", WHITE)],
        [],
        [("Hobbies: ", CYAN), ("...... ", MUTED),
         ("Photography, Malayalam type design, Malayalam cinema", WHITE)],
        [("Projects: ", CYAN), ("..... ", MUTED),
         ("Astroid bot, Stellar Media Organizer, Foldpix, Thenmavu font", WHITE)],
        [],
        [("— Contact —", CYAN)],
        [("Website: ", CYAN), ("...... ", MUTED), ("sharvinzlife.com", WHITE)],
        [("Instagram: ", CYAN), (".... ", MUTED), ("sharvinzlife", WHITE)],
        [("Facebook: ", CYAN), ("..... ", MUTED), ("sharvinzlife", WHITE)],
        [],
        [("— GitHub Stats —", CYAN)],
        [("Repos: ", CYAN), ("........ ", MUTED), (f"{stats['repos']:,}", WHITE),
         ("  |  ", MUTED), ("Stars: ", CYAN), ("...... ", MUTED), (f"{stats['stars']:,}", WHITE)],
        [("Commits: ", CYAN), ("...... ", MUTED), (f"{stats['commits']:,}", WHITE),
         ("  |  ", MUTED), ("Followers: ", CYAN), (".. ", MUTED),
         (f"{stats['followers']:,}", WHITE)],
        [("Lines of code:", CYAN), ("  ", MUTED), (f"{stats['loc']:,}", WHITE)],
    ]


def build_svg(stats, today=date.today()):
    for key in ("repos", "commits", "stars", "followers", "loc"):
        if not isinstance(stats.get(key), int) or isinstance(stats.get(key), bool):
            raise ValueError(f"stats[{key!r}] must be an int")

    info = _info_lines(stats, today)
    content = max(PORTRAIT_ROWS * ROW_STEP, len(info) * INFO_STEP)
    h = TOP + content + PAD

    portrait_svg = []
    for i, row in enumerate(ascii_portrait()):
        y = TOP + FONT + i * ROW_STEP
        runs = []
        j = 0
        while j < len(row):
            col = row[j][1]
            k = j
            while k < len(row) and row[k][1] == col:
                k += 1
            chars = "".join(c[0] for c in row[j:k])
            runs.append(f'<tspan fill="{col if col else "none"}">{chars}</tspan>')
            j = k
        portrait_svg.append(
            f'<text x="{PORT_X}" y="{y}" font-family="{MONO}" font-size="{FONT}" '
            f'xml:space="preserve">{"".join(runs)}</text>'
        )

    styles, reduced, info_svg = [], [], []
    for j, segs in enumerate(info):
        y = TOP + FONT + j * INFO_STEP
        styles.append(f".ln{j}{{animation:fade .5s ease {0.03 * j:.2f}s both}}")
        reduced.append(f".ln{j}{{animation:none;opacity:1}}")
        inner = "".join(
            f'<tspan fill="{s[1]}"' + (f' font-weight="{s[2]}"' if len(s) > 2 else "") +
            f'>{s[0]}</tspan>'
            for s in segs
        )
        info_svg.append(
            f'<text class="ln{j}" x="{INFO_X}" y="{y}" font-family="{MONO}" '
            f'font-size="{FONT}" xml:space="preserve">{inner}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" fill="none" role="img" aria-label="sharvin@streamwave neofetch card: ASCII portrait, stack, hobbies, contact and live GitHub stats.">
<defs>
<style>
  @keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
  {"".join(styles)}
  @media (prefers-reduced-motion: reduce){{
    {"".join(reduced)}
  }}
</style>
</defs>

<rect width="{W}" height="{h}" rx="6" fill="{BG}" stroke="{FRAME}"/>
{"".join(portrait_svg)}
{"".join(info_svg)}
</svg>
'''


def main():
    with open("assets/src/stats.json") as fh:
        stats = json.load(fh)
    svg = build_svg(stats)
    with open("assets/neofetch.svg", "w") as fh:
        fh.write(svg)
    print(f"wrote assets/neofetch.svg ({len(svg)} bytes)")


if __name__ == "__main__":
    main()

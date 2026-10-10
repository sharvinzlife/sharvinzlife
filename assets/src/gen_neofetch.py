#!/usr/bin/env python3
"""Neofetch-style profile card: colour ASCII portrait + GitHub stats.

Replaces the hero/boot banners. Reads assets/src/portrait.ppm (a pre-cropped
P3 image) and assets/src/stats.json (written by fetch_stats.py).

Two geometries share one renderer: WIDE (portrait beside the info column) for
the README, NARROW (info stacked under the portrait) for phones.
"""
import json
import math
import textwrap
from collections import namedtuple
from datetime import date, timedelta

MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

BG, PANE = "#04060b", "#070d16"
FRAME, MUTED = "#16405e", "#5b768c"
CYAN, WHITE = "#22d3ee", "#e6edf3"

RAMP_INV = "@%#*+=-:. "

PORTRAIT_ROWS = 58
PORTRAIT_COLS = 81

Layout = namedtuple("Layout", [
    "name", "width",
    "portrait_x", "portrait_font", "portrait_row_step", "portrait_char_step",
    "portrait_top",
    "info_x", "info_font", "info_step", "max_chars",
    "info_below", "gap", "pad",
])

WIDE = Layout(
    name="wide", width=1200,
    portrait_x=30, portrait_font=10, portrait_row_step=11, portrait_char_step=6.02,
    portrait_top=40,
    info_x=540, info_font=18, info_step=26, max_chars=58,
    info_below=False, gap=0, pad=40,
)

NARROW = Layout(
    name="narrow", width=600,
    portrait_x=(600 - 81 * 6.62) / 2, portrait_font=11, portrait_row_step=12.1,
    portrait_char_step=6.62, portrait_top=30,
    info_x=30, info_font=21, info_step=30, max_chars=43,
    info_below=True, gap=40, pad=40,
)


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
            ch = RAMP_INV[min(9, int(l / 256 * 10))]
            row.append((ch, WHITE))
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


def _wrapped(segments, value, color, layout):
    """A key/leader prefix plus a value, wrapped at word boundaries.

    Continuation lines are indented with spaces to the value column so the
    card still reads as a two-column key/value table.
    """
    column = sum(len(seg[0]) for seg in segments)
    chunks = textwrap.wrap(value, layout.max_chars - column) or [""]
    lines = [segments + [(chunks[0], color)]]
    for chunk in chunks[1:]:
        lines.append([(" " * column + chunk, color)])
    return lines


def _kv(key, leader, value, layout, color=WHITE):
    segments = [(key, CYAN)]
    if leader:
        segments.append((leader, MUTED))
    return _wrapped(segments, value, color, layout)


def _info_lines(stats, today, layout):
    lines = [
        [("sharvin@streamwave", CYAN, 700)],
        [("------------------", MUTED)],
    ]
    lines += _kv("OS: ", "........... ", "macOS, Debian 13, Unraid", layout)
    lines += _kv("Uptime: ", "....... ", uptime("2020-11-11", today), layout)
    lines += _kv("Host: ", "......... ", "Streamwave home lab · OCI edge", layout)
    lines += _kv("Kernel: ", "....... ", "AI Systems Engineer", layout)
    lines += _kv("IDE: ", ".......... ", "Claude Code, VS Code", layout)
    lines.append([])
    lines += _wrapped(
        [("Languages.Programming: ", CYAN)],
        "Go, Python, TypeScript, Rust, Kotlin", WHITE, layout,
    )
    lines += _kv("Languages.Real: ", "....... ", "English, Malayalam", layout)
    lines.append([])
    lines += _kv(
        "Hobbies: ", "...... ",
        "Photography, Malayalam type design, Malayalam cinema", layout,
    )
    lines += _kv(
        "Projects: ", "..... ",
        "Astroid bot, Stellar Media Organizer, Foldpix, Thenmavu font", layout,
    )
    lines.append([])
    lines.append([("— Contact —", CYAN)])
    lines += _kv("Website: ", "...... ", "sharvinzlife.com", layout)
    lines += _kv("Instagram: ", ".... ", "sharvinzlife", layout)
    lines += _kv("Facebook: ", "..... ", "sharvinzlife", layout)
    lines.append([])
    lines.append([("— GitHub Stats —", CYAN)])
    if layout.info_below:
        lines += _kv("Repos: ", "........ ", f"{stats['repos']:,}", layout)
        lines += _kv("Stars: ", "...... ", f"{stats['stars']:,}", layout)
        lines += _kv("Commits: ", "...... ", f"{stats['commits']:,}", layout)
        lines += _kv("Followers: ", ".. ", f"{stats['followers']:,}", layout)
        lines += _kv("Lines of code:", "  ", f"{stats['loc']:,}", layout)
    else:
        lines.append([
            ("Repos: ", CYAN), ("........ ", MUTED), (f"{stats['repos']:,}", WHITE),
            ("  |  ", MUTED), ("Stars: ", CYAN), ("...... ", MUTED),
            (f"{stats['stars']:,}", WHITE),
        ])
        lines.append([
            ("Commits: ", CYAN), ("...... ", MUTED), (f"{stats['commits']:,}", WHITE),
            ("  |  ", MUTED), ("Followers: ", CYAN), (".. ", MUTED),
            (f"{stats['followers']:,}", WHITE),
        ])
        lines.append([
            ("Lines of code:", CYAN), ("  ", MUTED), (f"{stats['loc']:,}", WHITE),
        ])
    return lines


def _info_top(layout):
    if layout.info_below:
        return (
            layout.portrait_top
            + PORTRAIT_ROWS * layout.portrait_row_step
            + layout.gap
        )
    return layout.portrait_top


def _content_height(layout, info_count):
    info_bottom = _info_top(layout) + info_count * layout.info_step
    if layout.info_below:
        return info_bottom
    portrait_bottom = layout.portrait_top + PORTRAIT_ROWS * layout.portrait_row_step
    return max(portrait_bottom, info_bottom)


def build_svg(stats, layout=WIDE, today=date.today()):
    for key in ("repos", "commits", "stars", "followers", "loc"):
        if not isinstance(stats.get(key), int) or isinstance(stats.get(key), bool):
            raise ValueError(f"stats[{key!r}] must be an int")

    info = _info_lines(stats, today, layout)
    h = math.ceil(_content_height(layout, len(info))) + layout.pad
    info_top = _info_top(layout)

    portrait_svg = []
    for i, row in enumerate(ascii_portrait()):
        y = layout.portrait_top + layout.portrait_font + i * layout.portrait_row_step
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
            f'<text x="{layout.portrait_x}" y="{y}" font-family="{MONO}" '
            f'font-size="{layout.portrait_font}" '
            f'xml:space="preserve">{"".join(runs)}</text>'
        )

    styles, reduced, info_svg = [], [], []
    for j, segs in enumerate(info):
        y = info_top + layout.info_font + j * layout.info_step
        styles.append(f".ln{j}{{animation:fade .5s ease {0.03 * j:.2f}s both}}")
        reduced.append(f".ln{j}{{animation:none;opacity:1}}")
        inner = "".join(
            f'<tspan fill="{s[1]}"' + (f' font-weight="{s[2]}"' if len(s) > 2 else "") +
            f'>{s[0]}</tspan>'
            for s in segs
        )
        info_svg.append(
            f'<text class="ln{j}" x="{layout.info_x}" y="{y}" font-family="{MONO}" '
            f'font-size="{layout.info_font}" xml:space="preserve">{inner}</text>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {layout.width} {h}" width="{layout.width}" height="{h}" fill="none" role="img" aria-label="sharvin@streamwave neofetch card: ASCII portrait, stack, hobbies, contact and live GitHub stats.">
<defs>
<style>
  @keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
  {"".join(styles)}
  @media (prefers-reduced-motion: reduce){{
    {"".join(reduced)}
  }}
</style>
</defs>

<rect width="{layout.width}" height="{h}" rx="6" fill="{BG}" stroke="{FRAME}"/>
{"".join(portrait_svg)}
{"".join(info_svg)}
</svg>
'''


def main():
    with open("assets/src/stats.json") as fh:
        stats = json.load(fh)
    for layout, path in (
        (WIDE, "assets/neofetch.svg"),
        (NARROW, "assets/neofetch-narrow.svg"),
    ):
        svg = build_svg(stats, layout=layout)
        with open(path, "w") as fh:
            fh.write(svg)
        print(f"wrote {path} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()

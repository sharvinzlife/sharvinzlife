#!/usr/bin/env python3
"""Self-hosted telemetry panel — replaces github-readme-stats, which 503s.

Numbers are real: language split measured across the author's public AND private
repositories (public-only would show Java/C# and omit Go entirely, since the
flagship repos are private).
"""
W, H = 1200, 356
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

BG, PANE = "#04060b", "#070d16"
FRAME, MUTED = "#16405e", "#5b768c"
CYAN, WHITE = "#22d3ee", "#e6edf3"
TRACK = "#0c1c2b"

# (language, percent, linguist colour)
LANGS = [
    ("Go",         47.3, "#00ADD8"),
    ("Python",     23.7, "#5fa9e8"),
    ("TypeScript", 18.8, "#3178C6"),
    ("Shell",       2.5, "#89e051"),
    ("JavaScript",  2.2, "#f1e05a"),
    ("Other",       5.5, "#7d5bbe"),
]

# (value, label) — every one of these is verifiable
CELLS = [
    ("2020",  "SHIPPING SINCE"),
    ("10",    "LANGUAGES SHIPPED"),
    ("5",     "LLM PROVIDERS ROUTED"),
    ("24/7",  "PRODUCTION UPTIME"),
]

BAR_X0, BAR_X1 = 250, 1128
BAR_W = BAR_X1 - BAR_X0
ROW_Y0, ROW_H = 176, 29

cells = []
cw = (1128 - 72) / 4
for i, (val, lab) in enumerate(CELLS):
    x = 72 + i * cw
    cells.append(
        f'<rect x="{x:.0f}" y="86" width="{cw-14:.0f}" height="60" rx="4" fill="{PANE}" '
        f'stroke="{FRAME}"/>'
        f'<text class="cell{i}" x="{x+16:.0f}" y="119" fill="{CYAN}" font-family="{MONO}" '
        f'font-size="24" font-weight="700">{val}</text>'
        f'<text x="{x+16:.0f}" y="136" fill="{MUTED}" font-family="{MONO}" font-size="9" '
        f'letter-spacing="1.6">{lab}</text>'
    )

bars, styles = [], []
for i, (name, pct, col) in enumerate(LANGS):
    y = ROW_Y0 + i * ROW_H
    w = BAR_W * pct / 100
    styles.append(
        f".b{i}{{animation:g{i} 1.5s cubic-bezier(.16,1,.3,1) {0.12*i+0.25:.2f}s both}}"
        f"@keyframes g{i}{{from{{width:0}}to{{width:{w:.1f}px}}}}"
    )
    bars.append(
        f'<text x="72" y="{y+11}" fill="{WHITE}" font-family="{MONO}" font-size="12.5" '
        f'font-weight="600">{name}</text>'
        f'<rect x="{BAR_X0}" y="{y}" width="{BAR_W}" height="14" rx="7" fill="{TRACK}"/>'
        f'<rect class="b{i}" x="{BAR_X0}" y="{y}" width="0" height="14" rx="7" fill="{col}"/>'
        f'<text class="p{i}" x="{BAR_X0-14}" y="{y+11}" fill="{col}" font-family="{MONO}" '
        f'font-size="12" font-weight="700" text-anchor="end">{pct:.1f}%</text>'
    )
    styles.append(
        f".p{i}{{animation:fade 0.5s ease {0.12*i+0.55:.2f}s both}}"
    )

reduced = "".join(
    f".b{i}{{animation:none;width:{BAR_W*p/100:.1f}px}}.p{i}{{animation:none;opacity:1}}"
    for i, (_, p, _) in enumerate(LANGS)
)

SVG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" aria-label="Telemetry: source distribution across public and private repositories — Go 47.3 percent, Python 23.7 percent, TypeScript 18.8 percent, Shell 2.5 percent, JavaScript 2.2 percent, other 5.5 percent. Shipping since 2020, 10 languages shipped, 5 LLM providers routed, 24/7 production uptime.">
<defs>
<radialGradient id="tglow" cx="80%" cy="0%" r="85%">
  <stop offset="0%" stop-color="#0d3350" stop-opacity="0.45"/>
  <stop offset="100%" stop-color="#04060b" stop-opacity="0"/>
</radialGradient>
<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="#fff" stop-opacity="0"/>
  <stop offset="50%" stop-color="#fff" stop-opacity="0.22"/>
  <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<style>
  {"".join(styles)}
  @keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
  .cell0,.cell1,.cell2,.cell3{{animation:fade .5s ease both}}
  .cell1{{animation-delay:.08s}} .cell2{{animation-delay:.16s}} .cell3{{animation-delay:.24s}}
  .shine{{animation:slide 4.5s linear infinite}}
  @keyframes slide{{0%{{transform:translateX(-320px)}}100%{{transform:translateX({W}px)}}}}
  @media (prefers-reduced-motion: reduce){{
    {reduced}
    .cell0,.cell1,.cell2,.cell3{{animation:none;opacity:1}}
    .shine{{animation:none;opacity:0}}
  }}
</style>
</defs>

<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="10" fill="url(#tglow)"/>

<text x="72" y="48" fill="{CYAN}" font-family="{MONO}" font-size="11" letter-spacing="4">[ 05 ] // TELEMETRY</text>
<text x="72" y="68" fill="{MUTED}" font-family="{MONO}" font-size="11">source distribution across public + private repositories</text>
<line x1="72" y1="{ROW_Y0-24}" x2="{BAR_X1}" y2="{ROW_Y0-24}" stroke="{FRAME}"/>

{"".join(cells)}
{"".join(bars)}

<rect class="shine" x="0" y="0" width="320" height="{H}" fill="url(#shine)" opacity="0.35"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{FRAME}"/>
</svg>
'''

out = "/Users/sharvin/projects/sharvinzlife-profile/assets/telemetry.svg"
open(out, "w").write(SVG)
print(f"wrote {out} ({len(SVG)} bytes)")

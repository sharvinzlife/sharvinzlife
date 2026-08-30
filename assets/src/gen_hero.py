#!/usr/bin/env python3
"""Generate the SHARVIN.OS animated HUD banner as a self-contained SVG.

Constraints (GitHub README):
  - no <script>, no external refs (camo blocks them), no web fonts
  - animation via internal <style> CSS + SMIL only
"""
import math
import random

W, H = 1200, 380
random.seed(69)  # 'curious69'

MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

BG      = "#04060b"
GRID    = "#0d2136"
FRAME   = "#16405e"
CYAN    = "#22d3ee"
CYAN_DIM= "#0e7490"
WHITE   = "#e6edf3"
MUTED   = "#5b768c"
AMBER   = "#f5a524"
GLITCH_R= "#ff2d55"
GLITCH_C= "#00fff0"

NAME = "JOSE SHARVIN"
ROLE = "AI SYSTEMS ENGINEER"


def grid():
    out = []
    for x in range(0, W + 1, 40):
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>')
    for y in range(0, H + 1, 40):
        out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>')
    return f'<g class="grid" stroke="{GRID}" stroke-width="1" mask="url(#fade)">{"".join(out)}</g>'


def particles(n=52):
    out = []
    for _ in range(n):
        x = random.uniform(10, W - 10)
        y = random.uniform(10, H - 10)
        r = random.choice([0.8, 1.0, 1.2, 1.6, 2.0])
        dur = random.uniform(7, 18)
        delay = random.uniform(0, 12)
        rise = random.uniform(30, 110)
        col = CYAN if random.random() < 0.62 else WHITE
        op = random.uniform(0.25, 0.85)
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" opacity="0">'
            f'<animate attributeName="opacity" values="0;{op:.2f};{op:.2f};0" '
            f'dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 -{rise:.0f}" dur="{dur:.1f}s" begin="{delay:.1f}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
    return f'<g class="particles">{"".join(out)}</g>'


def corners(pad=14, arm=34, sw=2):
    x0, y0, x1, y1 = pad, pad, W - pad, H - pad
    p = [
        f"M{x0} {y0+arm} L{x0} {y0} L{x0+arm} {y0}",
        f"M{x1-arm} {y0} L{x1} {y0} L{x1} {y0+arm}",
        f"M{x1} {y1-arm} L{x1} {y1} L{x1-arm} {y1}",
        f"M{x0+arm} {y1} L{x0} {y1} L{x0} {y1-arm}",
    ]
    paths = "".join(f'<path d="{d}"/>' for d in p)
    return (
        f'<g stroke="{CYAN}" stroke-width="{sw}" fill="none" stroke-linecap="square" '
        f'class="brackets">{paths}</g>'
    )


def radar(cx=1012, cy=186, r=104):
    rings = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r*k:.0f}" fill="none" stroke="{FRAME}" '
        f'stroke-width="1" opacity="{0.9-0.15*i:.2f}"/>'
        for i, k in enumerate((1.0, 0.72, 0.44, 0.18))
    )
    cross = (
        f'<line x1="{cx-r}" y1="{cy}" x2="{cx+r}" y2="{cy}" stroke="{FRAME}" stroke-width="1"/>'
        f'<line x1="{cx}" y1="{cy-r}" x2="{cx}" y2="{cy+r}" stroke="{FRAME}" stroke-width="1"/>'
    )
    # rotating sweep wedge
    sweep = (
        f'<g transform="translate({cx} {cy})">'
        f'<path d="M0 0 L{r} 0 A{r} {r} 0 0 1 {r*math.cos(math.radians(52)):.1f} '
        f'{r*math.sin(math.radians(52)):.1f} Z" fill="url(#sweepGrad)">'
        f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" '
        f'dur="4.2s" repeatCount="indefinite"/></path>'
        f'<line x1="0" y1="0" x2="{r}" y2="0" stroke="{CYAN}" stroke-width="1.5" opacity="0.9">'
        f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" '
        f'dur="4.2s" repeatCount="indefinite"/></line>'
        f"</g>"
    )
    blips = ""
    for bx, by, d in ((0.42, -0.30, 0.0), (-0.55, 0.28, 1.4), (0.20, 0.60, 2.8)):
        px, py = cx + bx * r, cy + by * r
        blips += (
            f'<circle cx="{px:.0f}" cy="{py:.0f}" r="3" fill="{AMBER}">'
            f'<animate attributeName="opacity" values="0;1;1;0" dur="4.2s" '
            f'begin="{d}s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{px:.0f}" cy="{py:.0f}" r="3" fill="none" stroke="{AMBER}" stroke-width="1">'
            f'<animate attributeName="r" values="3;16" dur="4.2s" begin="{d}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.9;0" dur="4.2s" begin="{d}s" repeatCount="indefinite"/>'
            f"</circle>"
        )
    label = (
        f'<text x="{cx}" y="{cy+r+26}" fill="{MUTED}" font-family="{MONO}" font-size="10" '
        f'letter-spacing="3" text-anchor="middle">SCANNING // 7 MODELS LOADED</text>'
    )
    return f'<g opacity="0.95">{rings}{cross}{sweep}{blips}{label}</g>'


def glitch_name(x=70, y=168):
    """Three stacked text layers: red + cyan channel offsets over a white base."""
    def t(cls, fill, extra=""):
        return (
            f'<text class="{cls}" x="{x}" y="{y}" fill="{fill}" font-family="{MONO}" '
            f'font-size="64" font-weight="700" letter-spacing="2"{extra}>{NAME}</text>'
        )
    return (
        f'<g class="nameWrap">'
        f'{t("gR", GLITCH_R)}'
        f'{t("gC", GLITCH_C)}'
        f'{t("gW", WHITE)}'
        # slice displacement: two clipped copies that jump horizontally
        f'<g clip-path="url(#slice1)">{t("gS1", WHITE)}</g>'
        f'<g clip-path="url(#slice2)">{t("gS2", GLITCH_C)}</g>'
        f"</g>"
    )


def typed_role(x=72, y=212):
    return (
        f'<g clip-path="url(#typeClip)">'
        f'<text x="{x}" y="{y}" fill="{CYAN}" font-family="{MONO}" font-size="21" '
        f'font-weight="600" letter-spacing="6">{ROLE}</text></g>'
        f'<rect class="caret" x="{x-3}" y="{y-17}" width="11" height="22" fill="{CYAN}"/>'
    )


def telemetry(y=310):
    chips = [
        ("ID · SHRVN-01", CYAN),
        ("LAT 42.78 · LON -83.24", MUTED),
        ("MI · US", MUTED),
        ("GO · TS · PY", MUTED),
    ]
    out, x = [], 72
    for text, col in chips:
        w = len(text) * 8.2 + 24
        out.append(
            f'<rect x="{x}" y="{y-15}" width="{w:.0f}" height="24" rx="3" fill="#081521" '
            f'stroke="{FRAME}" stroke-width="1"/>'
            f'<text x="{x+12}" y="{y+2}" fill="{col}" font-family="{MONO}" font-size="11" '
            f'letter-spacing="1.5">{text}</text>'
        )
        x += w + 10
    # live status with blinking dot
    out.append(
        f'<circle class="pulse" cx="{x+14}" cy="{y-3}" r="4" fill="#3fb950"/>'
        f'<text x="{x+26}" y="{y+2}" fill="#3fb950" font-family="{MONO}" font-size="11" '
        f'letter-spacing="1.5">SYSTEM ONLINE</text>'
    )
    return "".join(out)


SVG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" aria-label="Jose Sharvin — AI Systems Engineer. Multi-model orchestration, MCP tool-calling, self-hosted inference.">
<defs>
<linearGradient id="glow" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#0b3a52" stop-opacity="0.55"/>
  <stop offset="55%" stop-color="#04060b" stop-opacity="0"/>
</linearGradient>
<radialGradient id="vign" cx="30%" cy="40%" r="80%">
  <stop offset="0%" stop-color="#0a2438" stop-opacity="0.7"/>
  <stop offset="100%" stop-color="#04060b" stop-opacity="0"/>
</radialGradient>
<linearGradient id="sweepGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="{CYAN}" stop-opacity="0.42"/>
  <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
  <stop offset="50%" stop-color="{CYAN}" stop-opacity="0.5"/>
  <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="{CYAN}"/>
  <stop offset="100%" stop-color="#a855f7"/>
</linearGradient>
<mask id="fade">
  <rect width="{W}" height="{H}" fill="url(#fadeGrad)"/>
</mask>
<radialGradient id="fadeGrad" cx="35%" cy="45%" r="70%">
  <stop offset="0%" stop-color="#fff" stop-opacity="0.85"/>
  <stop offset="100%" stop-color="#fff" stop-opacity="0.05"/>
</radialGradient>
<clipPath id="typeClip"><rect class="typeRect" x="64" y="188" width="0" height="34"/></clipPath>
<clipPath id="slice1"><rect x="0" y="128" width="{W}" height="13"/></clipPath>
<clipPath id="slice2"><rect x="0" y="152" width="{W}" height="9"/></clipPath>
<style>
  .grid {{ animation: gridDrift 9s ease-in-out infinite alternate; }}
  @keyframes gridDrift {{ from {{ opacity:.55 }} to {{ opacity:.9 }} }}

  /* RGB chromatic aberration — mostly still, then a violent 300ms burst */
  .gR, .gC {{ opacity:.85; mix-blend-mode:screen; }}
  .gR {{ animation: chromaR 6.5s steps(1,end) infinite; }}
  .gC {{ animation: chromaC 6.5s steps(1,end) infinite; }}
  @keyframes chromaR {{
    0%,84% {{ transform:translate(0,0) }}   86% {{ transform:translate(-5px,2px) }}
    88%    {{ transform:translate(4px,-2px) }} 90% {{ transform:translate(-3px,0) }}
    92%    {{ transform:translate(2px,1px) }}  94%,100% {{ transform:translate(0,0) }}
  }}
  @keyframes chromaC {{
    0%,84% {{ transform:translate(0,0) }}   86% {{ transform:translate(5px,-2px) }}
    88%    {{ transform:translate(-4px,2px) }} 90% {{ transform:translate(3px,0) }}
    92%    {{ transform:translate(-2px,-1px) }} 94%,100% {{ transform:translate(0,0) }}
  }}
  /* horizontal slice tearing */
  .gS1 {{ animation: tear1 6.5s steps(1,end) infinite; }}
  .gS2 {{ animation: tear2 6.5s steps(1,end) infinite; }}
  @keyframes tear1 {{
    0%,85% {{ transform:translate(0,0); opacity:0 }}
    86%    {{ transform:translate(22px,0); opacity:1 }}
    89%    {{ transform:translate(-14px,0); opacity:1 }}
    91%    {{ transform:translate(8px,0); opacity:1 }}
    93%,100% {{ transform:translate(0,0); opacity:0 }}
  }}
  @keyframes tear2 {{
    0%,86% {{ transform:translate(0,0); opacity:0 }}
    87%    {{ transform:translate(-26px,0); opacity:1 }}
    90%    {{ transform:translate(16px,0); opacity:1 }}
    92%,100% {{ transform:translate(0,0); opacity:0 }}
  }}
  .nameWrap {{ animation: flicker 6.5s linear infinite; }}
  @keyframes flicker {{
    0%,84% {{ opacity:1 }} 85% {{ opacity:.55 }} 86% {{ opacity:1 }}
    89% {{ opacity:.7 }} 90%,100% {{ opacity:1 }}
  }}

  /* typing reveal + caret */
  .typeRect {{ animation: typeIn 6.5s steps(19,end) infinite; }}
  @keyframes typeIn {{ 0% {{ width:0 }} 42%,100% {{ width:370px }} }}
  .caret {{ animation: caretMove 6.5s steps(19,end) infinite, blink 1s steps(1,end) infinite; }}
  @keyframes caretMove {{ 0% {{ transform:translateX(0) }} 42%,100% {{ transform:translateX(353px) }} }}
  @keyframes blink {{ 0%,50% {{ opacity:1 }} 51%,100% {{ opacity:0 }} }}

  .scan {{ animation: scanY 5.5s cubic-bezier(.5,0,.5,1) infinite; }}
  @keyframes scanY {{ 0% {{ transform:translateY(-40px) }} 100% {{ transform:translateY(400px) }} }}

  .brackets {{ animation: bpulse 3.2s ease-in-out infinite; }}
  @keyframes bpulse {{ 0%,100% {{ opacity:.55 }} 50% {{ opacity:1 }} }}

  .pulse {{ animation: dot 1.6s ease-in-out infinite; }}
  @keyframes dot {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.25 }} }}

  .boot {{ animation: bootBar 6.5s ease-out infinite; }}
  @keyframes bootBar {{ 0% {{ width:0 }} 55%,100% {{ width:1056px }} }}

  @media (prefers-reduced-motion: reduce) {{
    .grid,.gR,.gC,.gS1,.gS2,.nameWrap,.typeRect,.caret,.scan,.brackets,.pulse,.boot
      {{ animation: none !important; }}
    .typeRect {{ width:370px }} .caret {{ opacity:0 }} .boot {{ width:1056px }}
  }}
</style>
</defs>

<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="10" fill="url(#vign)"/>
{grid()}
<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>
{particles()}
{radar()}

<!-- top rail -->
<text x="72" y="60" fill="{CYAN}" font-family="{MONO}" font-size="12" letter-spacing="5">[ SHARVIN.OS ]</text>
<text x="{W-72}" y="60" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="3" text-anchor="end">BUILD 2026.08 // IDENTITY CONFIRMED</text>
<line x1="72" y1="76" x2="{W-72}" y2="76" stroke="{FRAME}" stroke-width="1"/>

{glitch_name()}
{typed_role()}

<text x="72" y="252" fill="{MUTED}" font-family="{MONO}" font-size="13" letter-spacing="1">multi-model orchestration &#183; MCP tool-calling &#183; RAG &#183; self-hosted inference</text>

<!-- boot bar -->
<rect x="72" y="272" width="1056" height="3" rx="1.5" fill="#0c1c2b"/>
<rect class="boot" x="72" y="272" width="0" height="3" rx="1.5" fill="url(#barGrad)"/>

{telemetry()}

<!-- scanline + frame on top -->
<rect class="scan" x="0" y="0" width="{W}" height="46" fill="url(#scanGrad)" opacity="0.55"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{FRAME}" stroke-width="1"/>
{corners()}
</svg>
'''

out = "/Users/sharvin/projects/sharvinzlife-profile/assets/hero.svg"
with open(out, "w") as f:
    f.write(SVG)
print(f"wrote {out} ({len(SVG)} bytes)")

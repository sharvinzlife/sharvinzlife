#!/usr/bin/env python3
"""SHARVIN.OS boot sequence — a terminal that types itself out, line by line.

Same GitHub-README constraints as the hero: self-contained, no script, no webfonts.
"""
W, H = 1200, 500
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

BG, PANE = "#04060b", "#070d16"
FRAME, MUTED = "#16405e", "#5b768c"
CYAN, WHITE = "#22d3ee", "#e6edf3"
GREEN, AMBER, PURPLE = "#3fb950", "#f5a524", "#a855f7"

FS = 14.5
ADV = FS * 0.6  # monospace advance width
X0, Y0, LH = 56, 128, 33
LOOP = 11.0     # full cycle seconds
STEP = 0.34     # gap between lines
TYPE = 0.28     # time to type one line

# (badge, badge_colour, label, value, value_colour)
LINES = [
    ("$", CYAN, "./sharvin.os", "--init --verbose", MUTED),
    ("OK", GREEN, "identity", "JOSE SHARVIN  ·  ID SHRVN-01", WHITE),
    ("OK", GREEN, "role", "AI SYSTEMS ENGINEER  ·  MI, US", CYAN),
    ("OK", GREEN, "mounting /stack", "GO  ·  TYPESCRIPT  ·  PYTHON  ·  KOTLIN  ·  C#", WHITE),
    ("OK", GREEN, "llm routing", "GROQ · GEMINI · ANTHROPIC · MISTRAL · DEEPSEEK", WHITE),
    ("OK", GREEN, "local inference", "RTX 3090  ·  QWEN  ·  OLLAMA  ·  llama.cpp", WHITE),
    ("OK", GREEN, "protocols", "MCP  ·  RAG  ·  TOOL-CALLING  ·  whatsmeow", WHITE),
    ("OK", GREEN, "infra", "UNRAID  ·  DOCKER  ·  OCI  ·  CLOUDFLARE TUNNELS", WHITE),
    ("~~", AMBER, "in build", "ASTROID VOICE // zero-shot Malayalam TTS", AMBER),
    ("»", PURPLE, "status", "SHIPPING. ALWAYS.", PURPLE),
]

LABEL_COL = 30    # chars reserved for label + leader dots
BADGE_COL = 8


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


rows, styles = [], []
for i, (badge, bcol, label, value, vcol) in enumerate(LINES):
    y = Y0 + i * LH
    # [ OK ] badge
    btxt = f"[ {badge} ]" if badge not in ("$",) else "  $  "
    leader = "." * max(2, LABEL_COL - len(label) - 1)
    plain = f"{btxt} {label} {leader} {value}"
    # rightmost extent measured in advance-widths from X0, not len(plain):
    # the badge occupies BADGE_COL columns even though "[ OK ] " is 7 chars
    full_w = (BADGE_COL + len(label) + 1 + len(leader) + 1 + len(value)) * ADV + 10

    bx = X0
    lx = bx + BADGE_COL * ADV
    dx = lx + (len(label) + 1) * ADV
    vx = dx + (len(leader) + 1) * ADV

    rows.append(
        f'<g clip-path="url(#c{i})">'
        f'<text x="{bx}" y="{y}" fill="{bcol}" font-family="{MONO}" font-size="{FS}" '
        f'font-weight="700" xml:space="preserve">{esc(btxt)}</text>'
        f'<text x="{lx}" y="{y}" fill="{MUTED}" font-family="{MONO}" font-size="{FS}" '
        f'xml:space="preserve">{esc(label)}</text>'
        f'<text x="{dx}" y="{y}" fill="#123246" font-family="{MONO}" font-size="{FS}" '
        f'xml:space="preserve">{esc(leader)}</text>'
        f'<text x="{vx}" y="{y}" fill="{vcol}" font-family="{MONO}" font-size="{FS}" '
        f'font-weight="600" xml:space="preserve">{esc(value)}</text>'
        f"</g>"
    )

    start = (i * STEP) / LOOP * 100
    end = (i * STEP + TYPE) / LOOP * 100
    nsteps = max(4, len(plain) // 2)
    styles.append(
        f".c{i}{{animation:t{i} {LOOP}s steps({nsteps},end) infinite}}"
        f"@keyframes t{i}{{0%,{start:.2f}%{{width:0}}{end:.2f}%,100%{{width:{full_w:.0f}px}}}}"
    )

clips = "".join(
    f'<clipPath id="c{i}"><rect class="c{i}" x="{X0-4}" y="{Y0+i*LH-FS-4}" '
    f'width="0" height="{FS+12}"/></clipPath>'
    for i in range(len(LINES))
)

# blinking prompt cursor after the last line
cy = Y0 + len(LINES) * LH
cursor_at = (len(LINES) * STEP) / LOOP * 100
prompt = (
    f'<text class="prompt" x="{X0}" y="{cy}" fill="{CYAN}" font-family="{MONO}" '
    f'font-size="{FS}" font-weight="700">&#187;</text>'
    f'<rect class="cur" x="{X0+22}" y="{cy-FS+2}" width="9" height="{FS+2}" fill="{CYAN}"/>'
)

reduced = "".join(f".c{i}{{animation:none;width:9999px}}" for i in range(len(LINES)))

SVG = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" aria-label="SHARVIN.OS boot sequence: identity Jose Sharvin, AI Systems Engineer. Stack Go, TypeScript, Python, Kotlin, C-sharp. LLM routing across Groq, Gemini, Anthropic, Mistral, Deepseek. Local inference on RTX 3090 with Qwen, Ollama, llama.cpp. Protocols MCP, RAG, tool-calling. Infra Unraid, Docker, OCI, Cloudflare Tunnels. In build: Astroid Voice, zero-shot Malayalam TTS.">
<defs>
<radialGradient id="bglow" cx="18%" cy="0%" r="90%">
  <stop offset="0%" stop-color="#0d3350" stop-opacity="0.55"/>
  <stop offset="100%" stop-color="#04060b" stop-opacity="0"/>
</radialGradient>
<linearGradient id="titleBar" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0%" stop-color="#0a1926"/><stop offset="100%" stop-color="#070f19"/>
</linearGradient>
<linearGradient id="scan2" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
  <stop offset="50%" stop-color="{CYAN}" stop-opacity="0.30"/>
  <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
</linearGradient>
<pattern id="crt" width="1" height="3" patternUnits="userSpaceOnUse">
  <rect width="1" height="1" fill="#7dd3fc" opacity="0.030"/>
</pattern>
{clips}
<style>
  {"".join(styles)}
  .cur{{animation:blink2 1s steps(1,end) infinite, show {LOOP}s steps(1,end) infinite}}
  .prompt{{animation:show {LOOP}s steps(1,end) infinite}}
  @keyframes blink2{{0%,50%{{opacity:1}}51%,100%{{opacity:0}}}}
  @keyframes show{{0%,{cursor_at:.2f}%{{opacity:0}}{cursor_at+0.1:.2f}%,100%{{opacity:1}}}}
  .scanline2{{animation:sweep2 7s linear infinite}}
  @keyframes sweep2{{0%{{transform:translateY(-60px)}}100%{{transform:translateY({H+40}px)}}}}
  .dot1,.dot2,.dot3{{animation:dotpulse 2.4s ease-in-out infinite}}
  .dot2{{animation-delay:.3s}} .dot3{{animation-delay:.6s}}
  @keyframes dotpulse{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
  @media (prefers-reduced-motion: reduce){{
    {reduced}
    .cur,.prompt,.scanline2,.dot1,.dot2,.dot3{{animation:none}}
    .cur{{opacity:0}} .prompt{{opacity:1}}
  }}
</style>
</defs>

<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
<rect width="{W}" height="{H}" rx="10" fill="url(#bglow)"/>

<!-- terminal chrome -->
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{PANE}" stroke="{FRAME}"/>
<path d="M0 10 A10 10 0 0 1 10 0 L{W-10} 0 A10 10 0 0 1 {W} 10 L{W} 52 L0 52 Z" fill="url(#titleBar)"/>
<line x1="0" y1="52" x2="{W}" y2="52" stroke="{FRAME}"/>
<circle class="dot1" cx="28" cy="26" r="5.5" fill="#ff5f57"/>
<circle class="dot2" cx="48" cy="26" r="5.5" fill="#febc2e"/>
<circle class="dot3" cx="68" cy="26" r="5.5" fill="#28c840"/>
<text x="{W/2}" y="31" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="3" text-anchor="middle">sharvin@streamwave &#8212; /dev/os &#8212; 120&#215;40</text>
<text x="{W-24}" y="31" fill="{FRAME}" font-family="{MONO}" font-size="12" text-anchor="end">&#9679;&#9679;&#9679;</text>

<text x="{X0}" y="88" fill="{MUTED}" font-family="{MONO}" font-size="11" letter-spacing="4">[ 01 ] // BOOT SEQUENCE</text>

{"".join(rows)}
{prompt}

<rect width="{W}" height="{H}" rx="10" fill="url(#crt)"/>
<rect class="scanline2" x="0" y="0" width="{W}" height="56" fill="url(#scan2)"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{FRAME}"/>
</svg>
'''

out = "/Users/sharvin/projects/sharvinzlife-profile/assets/boot.svg"
open(out, "w").write(SVG)
print(f"wrote {out} ({len(SVG)} bytes)")

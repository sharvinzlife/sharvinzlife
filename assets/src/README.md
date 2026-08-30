# Asset generators

The three SVGs in `assets/` are generated, not hand-edited. Edit the script, re-run it,
commit both the script and the SVG.

```bash
python3 assets/src/gen_hero.py       # → assets/hero.svg
python3 assets/src/gen_boot.py       # → assets/boot.svg
python3 assets/src/gen_telemetry.py  # → assets/telemetry.svg
```

No dependencies — standard library only.

## Constraints these files must respect

GitHub renders README HTML through a sanitizer and proxies every image through camo.
That imposes hard limits:

- **No `<script>`, no `<style>`, no `style=` in the README markdown.** All animation has
  to live *inside* the SVG files.
- **No external references inside the SVGs** — no web fonts, no remote images. Camo blocks
  them. Use system monospace stacks only.
- **Single newlines inside a paragraph become `<br>`** in GFM. Badge groups must stay on
  one line or they stack vertically.
- Every panel paints its **own dark background** so it reads correctly in both GitHub
  light and dark themes.
- Each SVG carries a `prefers-reduced-motion` block that freezes it in its finished state.

## Verifying a change

CSS animations can't be seeked from outside an `<img>`, so freeze them at a chosen phase
and screenshot:

```bash
python3 - <<'PY'
src = open('assets/hero.svg').read()
open('/tmp/frozen.svg','w').write(src.replace('</style>',
  '\n * {animation-play-state:paused !important; animation-delay:-5.63s !important;}\n</style>'))
PY
```

Then render `/tmp/frozen.svg` in a browser. `-5.63s` lands on the hero's glitch burst;
`-3.2s` lands on its settled state.

## Where the telemetry numbers come from

`gen_telemetry.py` percentages are measured across **public and private** repositories.
Public-only would report Python 71% / C# 8.9% / Java 7.2% and omit Go entirely, because
the flagship Go and TypeScript repos are private — an accurate-but-misleading picture.
Re-measure before changing them.

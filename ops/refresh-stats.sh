#!/usr/bin/env bash
# Daily stats refresh. Takes the clone directory as $1.
set -euo pipefail

dir="${1:?usage: refresh-stats.sh <clone-dir>}"

git -C "$dir" pull --ff-only

( cd "$dir" && python3 assets/src/fetch_stats.py )
( cd "$dir" && python3 assets/src/gen_neofetch.py )

if git -C "$dir" diff --quiet -- assets/neofetch.svg assets/src/stats.json; then
  echo "no change"
  exit 0
fi

git -C "$dir" add assets/neofetch.svg assets/src/stats.json
git -C "$dir" commit -m "chore(stats): daily refresh $(date +%F)"
git -C "$dir" push origin main

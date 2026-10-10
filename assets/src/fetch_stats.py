#!/usr/bin/env python3
"""Fetch GitHub stats for the neofetch card via the authenticated `gh` CLI.

Writes assets/src/stats.json only after every number is known.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date

OUT = "assets/src/stats.json"

BACKOFF = [2, 4, 8, 16, 30, 30, 30, 30]


def run_gh(args):
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout


def _status(text):
    m = re.match(r"HTTP/\S+\s+(\d+)", text.replace("\r\n", "\n"))
    if not m:
        raise RuntimeError(f"no HTTP status line in: {text[:80]!r}")
    return int(m.group(1))


def _body(text):
    normalized = text.replace("\r\n", "\n")
    i = normalized.find("\n\n")
    return normalized[i + 2:] if i >= 0 else normalized


def _parse_paginated(text):
    decoder = json.JSONDecoder()
    text = text.strip()
    out, i = [], 0
    while i < len(text):
        obj, j = decoder.raw_decode(text, i)
        out.extend(obj) if isinstance(obj, list) else out.append(obj)
        i = j
        while i < len(text) and text[i] in " \n\r\t":
            i += 1
    return out


def _cache_path():
    return os.path.expanduser(
        os.environ.get("PROFILE_STATS_CACHE", "~/.cache/profile-stats/loc.json")
    )


def _load_cache():
    try:
        with open(_cache_path()) as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def _save_cache(cache):
    path = _cache_path()
    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(cache, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def loc_for(repo, run=run_gh, cache=None, warnings=None, sleep=time.sleep):
    cache = {} if cache is None else cache
    warnings = [] if warnings is None else warnings
    for delay in BACKOFF:
        out = run(["api", "-i", f"repos/sharvinzlife/{repo}/stats/code_frequency"])
        status = _status(out)
        if status == 202:
            sleep(delay)
            continue
        if status == 204:
            return 0
        if status != 200:
            raise RuntimeError(f"{repo}: unexpected HTTP {status}")
        weeks = json.loads(_body(out) or "[]")
        value = sum(added + deleted for _, added, deleted in weeks)
        cache[repo] = value
        return value
    if repo in cache:
        warnings.append(f"{repo}: stats not ready, used cached loc {cache[repo]}")
        return cache[repo]
    raise RuntimeError(f"{repo}: stats not ready")


def commits_for(repo, size, run=run_gh):
    if size == 0:
        return 0
    out = run(["api", "-i", f"repos/sharvinzlife/{repo}/commits?per_page=1"])
    status = _status(out)
    if status != 200:
        raise RuntimeError(f"{repo}: unexpected HTTP {status}")
    headers = out.replace("\r\n", "\n").split("\n\n", 1)[0]
    m = re.search(r'page=(\d+)>;\s*rel="last"', headers, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return len(json.loads(_body(out) or "[]"))


def fetch_stats(run=run_gh, today=None, cache=None, warnings=None, sleep=time.sleep):
    today = today or date.today()
    cache = {} if cache is None else cache
    warnings = [] if warnings is None else warnings
    user = json.loads(run(["api", "user"]))
    owned = [r for r in _parse_paginated(
        run(["api", "user/repos?per_page=100&affiliation=owner", "--paginate"])
    ) if not r.get("fork")]
    for r in owned:
        run(["api", "-i", f"repos/sharvinzlife/{r['name']}/stats/code_frequency"])
    commits = sum(
        commits_for(r["name"], r.get("size", 0), run=run) for r in owned
    )
    loc = sum(
        loc_for(r["name"], run=run, cache=cache, warnings=warnings, sleep=sleep)
        for r in owned
    )
    return {
        "repos": len(owned),
        "commits": commits,
        "stars": sum(r.get("stargazers_count", 0) for r in owned),
        "followers": user["followers"],
        "loc": loc,
        "generated": today.isoformat(),
    }


def main():
    cache = _load_cache()
    warnings = []
    stats = fetch_stats(cache=cache, warnings=warnings)
    for warning in warnings:
        print(f"WARN {warning}", file=sys.stderr)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(OUT), suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(stats, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, OUT)
    _save_cache(cache)
    print(f"wrote {OUT}: {stats}")


if __name__ == "__main__":
    main()

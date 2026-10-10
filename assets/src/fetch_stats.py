#!/usr/bin/env python3
"""Fetch GitHub stats for the neofetch card via the authenticated `gh` CLI.

Writes assets/src/stats.json only after every number is known.
"""
import json
import os
import re
import subprocess
import tempfile
import time
from datetime import date

OUT = "assets/src/stats.json"

CONTRIBUTIONS_QUERY = (
    "query($from:DateTime!,$to:DateTime!){"
    "viewer{contributionsCollection(from:$from,to:$to){"
    "totalCommitContributions restrictedContributionsCount}}}"
)


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


def loc_for(repo, run=run_gh):
    for _ in range(10):
        out = run(["api", "-i", f"repos/sharvinzlife/{repo}/stats/code_frequency"])
        status = _status(out)
        if status == 202:
            time.sleep(3)
            continue
        if status == 204:
            return 0
        if status != 200:
            raise RuntimeError(f"{repo}: unexpected HTTP {status}")
        weeks = json.loads(_body(out) or "[]")
        return sum(added + deleted for _, added, deleted in weeks)
    raise RuntimeError(f"{repo}: stats not ready")


def _contributions(run, year):
    out = run([
        "api", "graphql",
        "-f", f"query={CONTRIBUTIONS_QUERY}",
        "-f", f"from={year}-01-01T00:00:00Z",
        "-f", f"to={year}-12-31T23:59:59Z",
    ])
    collection = json.loads(out)["data"]["viewer"]["contributionsCollection"]
    return collection["totalCommitContributions"] + collection["restrictedContributionsCount"]


def fetch_stats(run=run_gh, today=None):
    today = today or date.today()
    user = json.loads(run(["api", "user"]))
    owned = [r for r in _parse_paginated(
        run(["api", "user/repos?per_page=100&affiliation=owner", "--paginate"])
    ) if not r.get("fork")]
    commits = sum(
        _contributions(run, year)
        for year in range(int(user["created_at"][:4]), today.year + 1)
    )
    return {
        "repos": len(owned),
        "commits": commits,
        "stars": sum(r.get("stargazers_count", 0) for r in owned),
        "followers": user["followers"],
        "loc": sum(loc_for(r["name"], run=run) for r in owned),
        "generated": today.isoformat(),
    }


def main():
    stats = fetch_stats()
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(OUT), suffix=".tmp")
    with os.fdopen(fd, "w") as fh:
        json.dump(stats, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, OUT)
    print(f"wrote {OUT}: {stats}")


if __name__ == "__main__":
    main()

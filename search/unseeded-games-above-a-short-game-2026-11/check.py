#!/usr/bin/env python3
"""The checks of study B11's lines: every line of every file is unsound, every line that the study's build wrote is of
that build, on master 56dcbdd, no score is above the committed opt(n), and a game played twice has the better of its
plays.

    python3 -I check.py FILE...

Prints, for each file, its lines and the games it has, and any line that fails a check; exits with 1 if one does.
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optlib import opt_scores  # noqa: E402


def main():
    opt = opt_scores()
    failed = False
    for path in sys.argv[1:]:
        lines, ours, games, bad = 0, 0, set(), []
        with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
            for text in f:
                if not text.strip():
                    continue
                line = json.loads(text)
                lines += 1
                n = line["n"]
                games.add(n)
                if line.get("unsound") is not True:
                    bad.append((n, "not unsound"))
                if n in opt and line["score"] > opt[n]:
                    bad.append((n, f"score {line['score']} above opt(n) {opt[n]}"))
                # The study's build writes `unseeded`; the walk's files begin with E2's lines, of an older build.
                if "unseeded" in line:
                    ours += 1
                    if not line["build"]["commit"].startswith("56dcbdd"):
                        bad.append((n, f"build {line['build']}"))
                other = line.get("other")
                tie_kept_unseeded = other is not None and other["score"] == line["score"] and line["unseeded"]
                if other is not None and (other["score"] > line["score"] or other["unseeded"] == line["unseeded"]
                                          or tie_kept_unseeded):
                    bad.append((n, f"the other play {other} is not the worse one"))
        print(f"{path}: {lines} lines ({ours} of this build), {len(games)} games, {len(bad)} failing {bad[:5]}")
        failed |= bool(bad)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

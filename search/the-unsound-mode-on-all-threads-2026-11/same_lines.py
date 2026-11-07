#!/usr/bin/env python3
"""Whether files of unsound lines are the same but for what varies from run to run: the seconds, the threads and the
build.

    python3 -I same_lines.py FILE FILE...

Compares every file with the first, game by game, and prints for each the games it has and the first difference, if
there is one.  The exit status is 1 if any file differs.
"""

import json
import sys

# What a line may differ in between runs of the same game: its times, its threads and the build that made it.
VARYING = ("seconds", "start_seconds", "threads", "build")


def timeless(line):
    line = {key: value for key, value in line.items() if key not in VARYING}
    line["improvements"] = [{k: v for k, v in i.items() if k != "seconds"} for i in line.get("improvements") or []]
    return line


def lines(path):
    with open(path) as f:
        return {line["n"]: timeless(line) for line in map(json.loads, f)}


def main():
    first, *others = sys.argv[1:]
    base = lines(first)
    status = 0
    for other in others:
        theirs = lines(other)
        common = sorted(set(base) & set(theirs))
        differ = [n for n in common if base[n] != theirs[n]]
        if set(base) != set(theirs):
            print(f"{other}: games differ from {first}: {len(base)} against {len(theirs)}")
            status = 1
        if differ:
            n = differ[0]
            keys = [k for k in base[n] if base[n].get(k) != theirs[n].get(k)]
            print(f"{other}: {len(differ)} of {len(common)} games differ, the first n={n} in {keys}")
            status = 1
        else:
            print(f"{other}: the same as {first} in all {len(common)} games")
    sys.exit(status)


if __name__ == "__main__":
    main()

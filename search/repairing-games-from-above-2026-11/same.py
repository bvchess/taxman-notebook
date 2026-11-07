#!/usr/bin/env python3
"""Whether two files of unsound lines hold the same lines but for what varies from run to run.

    python3 -I same.py A B

Compares the files line by line, in order, without the keys that vary from run to run: the times (a line's `seconds` and
`start_seconds`, each improvement's `seconds`, a repair's `seconds`), the threads and the build.  Where one file has keys
the other lacks (a build without the repair), only the keys both have are compared.  Prints the count of lines and any
that differ, with the keys that differ.
"""

import gzip
import json
import sys

VARIES = {"seconds", "start_seconds", "threads", "build"}


def timeless(value):
    """`value` without the keys that vary from run to run, at any depth."""
    if isinstance(value, dict):
        return {k: timeless(v) for k, v in value.items() if k not in VARIES}
    if isinstance(value, list):
        return [timeless(v) for v in value]
    return value


def read(path):
    """The lines of the file at `path`, gzipped or not, without what varies from run to run."""
    with (gzip.open(path, "rt") if path.endswith(".gz") else open(path)) as f:
        return [timeless(json.loads(text)) for text in f]


def main():
    a, b = read(sys.argv[1]), read(sys.argv[2])
    differ = []
    for i, (x, y) in enumerate(zip(a, b)):
        keys = set(x) & set(y)
        bad = sorted(k for k in keys if x[k] != y[k])
        if bad:
            differ.append((i + 1, x.get("n"), bad))
    only = sorted((set(a[0]) ^ set(b[0]))) if a and b else []
    print(f"{len(a)} and {len(b)} lines; keys in one only: {only}; lines that differ: {differ or 'none'}")


if __name__ == "__main__":
    main()

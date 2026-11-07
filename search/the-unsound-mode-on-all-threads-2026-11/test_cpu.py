#!/usr/bin/env python3
"""The CPU seconds of each test of a test binary, each run as a process of its own, as the quick check runs them.

    python3 -I test_cpu.py CWD FILTER BINARY...

Lists the tests of each BINARY whose name contains FILTER, runs each alone (`--exact NAME --test-threads 1`) in CWD,
and prints its user and system CPU seconds, one column a binary, with the totals.
"""

import resource
import subprocess
import sys


def tests(binary, cwd, needle):
    out = subprocess.run([binary, "--list"], cwd=cwd, capture_output=True, text=True).stdout
    return [line[:-len(": test")] for line in out.splitlines() if line.endswith(": test") and needle in line]


def cpu(binary, cwd, name):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    subprocess.run([binary, "--exact", name, "--test-threads", "1"], cwd=cwd, capture_output=True)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return after.ru_utime - before.ru_utime + after.ru_stime - before.ru_stime


def main():
    cwd, needle, *binaries = sys.argv[1:]
    names = sorted(set.intersection(*(set(tests(b, cwd, needle)) for b in binaries)))
    totals = [0.0] * len(binaries)
    for name in names:
        row = [cpu(b, cwd, name) for b in binaries]
        totals = [t + r for t, r in zip(totals, row)]
        print(" ".join(f"{r:6.2f}" for r in row), name)
    print(" ".join(f"{t:6.2f}" for t in totals), "total")
    for b in binaries:
        extra = sorted(set(tests(b, cwd, needle)) - set(names))
        for name in extra:
            print(f"{cpu(b, cwd, name):6.2f} only in {b}: {name}")


if __name__ == "__main__":
    main()

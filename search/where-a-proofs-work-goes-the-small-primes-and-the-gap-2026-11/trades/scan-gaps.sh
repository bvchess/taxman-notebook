#!/bin/bash
# The gaps of restricted roots, with no search: each argument as for run-fix.sh, N:B:PART[:K[:SEED]], run with a limit
# of one step, so that the line gives the restricted root's GF(2) bound (its gap is bound - opt).  Lines in $OUT
# (default scan.jsonl).
set -u
cd "$(dirname "$0")"
OUT=${OUT:-scan.jsonl} NODES=1 LIMIT=60 ./run-fix.sh "$@"

#!/bin/bash
# Compares the panel runs: compare.sh BASE LABEL...  One row a game: nodes and seconds of each run, and whether the
# verdict and the nodes equal BASE's.
here=${NODECOST_DIR:-$(cd "$(dirname "$0")" && pwd)}/runs
base=$1
shift
for n in $(jq -r '.n' "$here/$base/out.jsonl"); do
    b=$(jq -c "select(.n==$n) | [.search, .nodes, .secs]" "$here/$base/out.jsonl" | tail -1)
    row="$n base $b"
    for label in "$@"; do
        r=$(jq -c "select(.n==$n) | [.search, .nodes, .secs]" "$here/$label/out.jsonl" 2>/dev/null | tail -1)
        if [ -z "$r" ]; then
            row="$row | $label -"
            continue
        fi
        same=$(jq -n --argjson a "$b" --argjson c "$r" 'if $a[0]==$c[0] and $a[1]==$c[1] then "same" else "DIFFERENT" end')
        ratio=$(jq -n --argjson a "$b" --argjson c "$r" '($c[2]/$a[2]*1000|round)/1000')
        row="$row | $label $r $same x$ratio"
    done
    echo "$row"
done

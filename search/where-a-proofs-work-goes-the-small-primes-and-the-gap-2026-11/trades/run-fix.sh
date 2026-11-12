#!/bin/bash
# The controls: game n with a part of its candidates fixed or barred as the committed optimal set of n has them and
# the rest free, an exact search on 16 threads at idle priority that must find opt(n) and prove nothing beats it.
# Each argument is N:B:PART[:K[:SEED[:c]]]: PART is "smooth" (the candidates whose primes are all at most B) or
# "rough" (the others), and K, if given and not "-", takes K of them at random with the seed SEED (default 1), or
# with a last field "c" the part's members not drawn.  One JSON line per run in $OUT (default fix.jsonl); a run
# already there is skipped.  NODES (default 30000000) limits each search's steps and LIMIT (default 600) its seconds.
set -u
cd "$(dirname "$0")"
R=./restricted
OUT=${OUT:-fix.jsonl}
NODES=${NODES:-30000000}
LIMIT=${LIMIT:-600}
for spec in "$@"; do
    IFS=: read -r n b part k seed comp <<< "$spec"
    k=${k:--}
    seed=${seed:-1}
    comp=${comp:-}
    args=(fix-smooth "$n" --smooth "$b" --threads 16 --background --node-limit "$NODES")
    args+=(--time-limit "$LIMIT" --tactic symmetry=off)
    rough=false
    [ "$part" = "rough" ] && { args+=(--rough); rough=true; }
    random=null
    [ "$k" != "-" ] && { args+=(--random "$k" --seed "$seed"); random=$k; }
    [ "$random" = "null" ] && seed=null
    [ "$comp" = "c" ] && args+=(--complement)
    key="{\"n\":$n,\"smooth\":$b,\"rough\":$rough,\"random\":$random,\"seed\":$seed,"
    if [ "$comp" = "c" ]; then
        grep -F "$key" "$OUT" 2>/dev/null | grep -qF '"complement":true' && continue
    else
        grep -F "$key" "$OUT" 2>/dev/null | grep -vqF '"complement":true' && continue
    fi
    chrt -i 0 nice -n 19 $R "${args[@]}" >> "$OUT" 2>> "fix-$n.err" || echo "failed: $spec" >> fix.failed
done
echo "done: $*" >> fix.done

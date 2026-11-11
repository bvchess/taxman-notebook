#!/bin/bash
# play.sh N LEVEL SEED: one play of game N into the shared best-known file, at idle priority on 12 threads, recorded in
# the root-first ledger (so the filler never repeats it); prints the known score and the new one
cd /home/brian/taxman_work/lab/work/rootfirst
n=$1 level=$2 seed=$3 out=plays/g$1-l$2-s$3
[ -e $out.jsonl ] && { echo "$n: already played at level $level, seed $seed"; exit 0; }
chrt -i 0 nice -n 19 ../unsound-run/taxman-aeffc29 solve $n-$n --unsound --stop-growth off \
    --best-known /home/brian/taxman_work/lab/work/unsound-run/best-known.jsonl --threads 12 --effort $level --seed $seed \
    --out $out.jsonl > $out.log 2>&1 < /dev/null || { echo "$n: the play failed ($out.log)"; exit 1; }
read -r known score < <(python3 -I -c "
import json, sys
last = [json.loads(t) for t in open(sys.argv[1]) if t.strip() and json.loads(t)['n'] == int(sys.argv[2])][-1]
print(last.get('known_before') or 0, last['score'])" $out.jsonl $n)
printf '%s\t%s\t%s\t%s\t%s\t%s\n' $n $level $seed "$known" "$score" "$(date +%T)" >> ledger2.tsv
echo "$n level $level seed $seed: $known -> $score ($((score - known)))"

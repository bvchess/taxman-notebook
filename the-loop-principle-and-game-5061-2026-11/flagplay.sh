#!/bin/bash
# flagplay.sh N: one level-4 play of game N on its first seed of 41-43 not yet played (succession/lawscan/play.sh, which
# records it in the root-first ledger), and, if it raises N, a line "gain at N," for the push-down watcher of
# rootfirst/targets-a.log.  For the games the loops brief flags (patterns_out.txt: a rise in a clean window).
n=$1
R=/home/brian/taxman_work/lab/work/rootfirst
for seed in 41 42 43; do
    [ -e $R/plays/g$n-l4-s$seed.jsonl ] || break
done
[ -e $R/plays/g$n-l4-s$seed.jsonl ] && { echo "$n: all three seeds played"; exit 0; }
line=$(/home/brian/taxman_work/lab/work/succession/lawscan/play.sh $n 4 $seed)
echo "$line $(date +%T)"
case "$line" in
    *"->"*"(0)") ;;
    *"->"*) echo "gain at $n, flagged by the loops brief" >> $R/targets-a.log ;;
esac

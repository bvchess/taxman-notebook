#!/bin/bash
# The measurement queue after the rebase onto c0d0d3e, one thread, nice 19, one run at a time.
# NOGOODS_DIR holds bin/ (the builds), out/ and ckpt/ (default: the script's folder).
S=${NOGOODS_DIR:-$(cd "$(dirname "$0")" && pwd)}
cd $S
GAMES="798 864 988 1309 1508 1771 1920 2033 2044 1548 1587 1612"
nice -n 19 bin/nogoodcheck-master2 0 $GAMES > out/fp-master2.txt 2>&1
nice -n 19 bin/nogoodcheck-rebased 0 $GAMES > out/fp-rebased.txt 2>&1
nice -n 19 bin/nogoodcheck-rebased 200000 1475 > out/long-rebased.txt 2>&1
./panel.sh $S/bin/exact-master2 panel-master2 988 1309 1508 1771 1920 2044 1548 1587 1612
./panel.sh $S/bin/exact-rebased panel-rebased 988 1309 1508 1771 1920 2044 1548 1587 1612
echo done > out/queue2.done

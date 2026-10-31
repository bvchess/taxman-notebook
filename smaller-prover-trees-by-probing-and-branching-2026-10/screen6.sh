#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1508 1309 1196"
B="probe=1,learn=1,order=1,fresh=2,pick=1"
$S/variant.sh $S/exact-study Bs50 $B,slope=50 $G
$S/variant.sh $S/exact-study Bs25 $B,slope=25 $G
$S/variant.sh $S/exact-study Bs10 $B,slope=10 $G
$S/variant.sh $S/exact-study Bs100l2 $B,slope=100,learn=2 $G
echo screen6 done

#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1508 1309 1196"
B="probe=1,learn=1,order=1,fresh=2,pick=1"
$S/variant.sh $S/exact-study B $B $G
$S/variant.sh $S/exact-study Bl2 $B,learn=2 $G
$S/variant.sh $S/exact-study Bp2 $B,probe=2 $G
$S/variant.sh $S/exact-study Bs100 $B,slope=100 $G
$S/variant.sh $S/exact-study Bs400 $B,slope=400 $G
echo screen5 done

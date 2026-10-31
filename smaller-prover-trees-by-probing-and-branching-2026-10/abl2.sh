#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1508 1309 1920 1040 2044"
$S/variant.sh $S/exact-abl2 bO2 order=2 $G
$S/variant.sh $S/exact-abl2 bO3 order=3 $G
$S/variant.sh $S/exact-abl2 bO0H0 order=0,hold=0 $G
$S/variant.sh $S/exact-abl2 bO0C4 order=0,cap=4 $G
$S/variant.sh $S/exact-abl2 bO0C32 order=0,cap=32 $G
echo abl2 done

#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1508 1309 1920 1040 2044"
$S/variant.sh $S/exact-abl2 cC1 order=0,cap=1 $G
$S/variant.sh $S/exact-abl2 cC2 order=0,cap=2 $G
$S/variant.sh $S/exact-abl2 cC3 order=0,cap=3 $G
$S/variant.sh $S/exact-abl2 cC6 order=0,cap=6 $G
echo abl3 done

#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1309 1508 1920"
$S/variant.sh $S/exact-study pr1l1o1f2 probe=1,learn=1,order=1,fresh=2 $G
$S/variant.sh $S/exact-study pr1l1p1o1f2 probe=1,learn=1,pick=1,order=1,fresh=2 $G
echo screen4 done

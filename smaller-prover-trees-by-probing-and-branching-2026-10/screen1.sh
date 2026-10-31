#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1000 1771 2030"
$S/variant.sh $S/exact-study v0 - $G
$S/variant.sh $S/exact-study l1 learn=1 $G
$S/variant.sh $S/exact-study l1p1 learn=1,pick=1 $G
$S/variant.sh $S/exact-study l1o1 learn=1,order=1 $G
$S/variant.sh $S/exact-study l1p1o1 learn=1,pick=1,order=1 $G
$S/variant.sh $S/exact-study pr1 probe=1 $G
$S/variant.sh $S/exact-study l1f1 learn=1,fresh=1 $G
$S/variant.sh $S/exact-study l1f2 learn=1,fresh=2 $G
echo screen1 done

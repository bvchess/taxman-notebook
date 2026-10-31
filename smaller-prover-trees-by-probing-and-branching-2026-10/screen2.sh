#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1000 1771 2030"
$S/variant.sh $S/exact-study pr1l1 probe=1,learn=1 $G
$S/variant.sh $S/exact-study pr1o1 probe=1,order=1 $G
$S/variant.sh $S/exact-study pr1l1o1 probe=1,learn=1,order=1 $G
$S/variant.sh $S/exact-study pr1l1p1o1 probe=1,learn=1,pick=1,order=1 $G
$S/variant.sh $S/exact-study pr1l1f1 probe=1,learn=1,fresh=1 $G
$S/variant.sh $S/exact-study pr1l1f2 probe=1,learn=1,fresh=2 $G
$S/variant.sh $S/exact-study pr1o3 probe=1,order=3 $G
$S/variant.sh $S/exact-study pr1o2 probe=1,order=2 $G
echo screen2 done

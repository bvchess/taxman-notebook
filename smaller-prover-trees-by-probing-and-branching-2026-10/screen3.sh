#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1040 1196 2044"
$S/variant.sh $S/exact-study pr1 probe=1 $G
$S/variant.sh $S/exact-study pr1l1o1 probe=1,learn=1,order=1 $G
$S/variant.sh $S/exact-study pr1l1o1f2 probe=1,learn=1,order=1,fresh=2 $G
$S/variant.sh $S/exact-study pr1l1p1o1f2 probe=1,learn=1,pick=1,order=1,fresh=2 $G
$S/variant.sh $S/exact-study pr1l1f2 probe=1,learn=1,fresh=2 $G
G="1000 1771 2030"
$S/variant.sh $S/exact-study pr1l1o1f2 probe=1,learn=1,order=1,fresh=2 $G
$S/variant.sh $S/exact-study pr1l1p1o1f2 probe=1,learn=1,pick=1,order=1,fresh=2 $G
echo screen3 done

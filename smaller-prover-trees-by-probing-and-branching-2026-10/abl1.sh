#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1508 1309 1920 1040 2044"
$S/variant.sh $S/exact-abl aF learn=0,hold=0,order=0,rank=0 $G
$S/variant.sh $S/exact-abl aA - $G
$S/variant.sh $S/exact-abl aB learn=0 $G
$S/variant.sh $S/exact-abl aC hold=0 $G
$S/variant.sh $S/exact-abl aD order=0 $G
$S/variant.sh $S/exact-abl aE rank=0 $G
$S/variant.sh $S/exact-abl aG learn=0,hold=0 $G
$S/variant.sh $S/exact-abl aH cap=4 $G
$S/variant.sh $S/exact-abl aI learn=0,hold=0,rank=0 $G
echo abl1 done

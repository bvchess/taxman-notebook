#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1575 1584 1600"
$S/variant.sh $S/exact-abl2 dF learn=0,hold=0,order=0,rank=0 $G
$S/variant.sh $S/exact-abl2 dBase order=0,cap=4 $G
$S/variant.sh $S/exact-abl2 dO1 order=1,cap=4 $G
$S/variant.sh $S/exact-abl2 dR0 order=0,cap=4,rank=0 $G
$S/variant.sh $S/exact-abl2 dH0 order=0,cap=4,hold=0 $G
$S/variant.sh $S/exact-abl2 dL1 order=0,cap=1 $G
$S/variant.sh $S/exact-abl2 dC16 order=0,cap=16 $G
$S/variant.sh $S/exact-abl2 dO2 order=2,cap=4 $G
echo abl4 done

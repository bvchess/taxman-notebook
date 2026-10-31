#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1000 1040 1196 1771 2030 2044 1309 1508 1920 936 950 988 1100 1190 1225 1254 1280 1575 1600 1770 1912 2025 2040 1584"
$S/variant.sh $S/exact-abl3 gC2 rank=2,slope=210,cap=2 $G
$S/variant.sh $S/exact-abl3 gC8 rank=2,slope=210,cap=8 $G
$S/variant.sh $S/exact-abl3 gH0 rank=2,slope=210,hold=0 $G
$S/variant.sh $S/exact-abl3 gC1 rank=2,slope=210,cap=1 $G
echo abl7 done

#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1000 1040 1196 1771 2030 2044 1309 1508 1920 936 950 988 1100 1190 1225 1254 1280 1575 1600 1770 1912 2025 2040 1584"
$S/variant.sh $S/exact-abl3 fR0 rank=0 $G
$S/variant.sh $S/exact-abl3 fW210 rank=2,slope=210 $G
$S/variant.sh $S/exact-abl3 fW400 rank=2,slope=400 $G
$S/variant.sh $S/exact-abl3 fL rank=1 $G
echo abl6 done

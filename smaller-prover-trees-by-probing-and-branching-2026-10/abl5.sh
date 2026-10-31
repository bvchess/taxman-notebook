#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
G="1575 1584 1600 1508 1309"
for s in 25 100 210 400; do
  $S/variant.sh $S/exact-abl3 eW$s rank=2,slope=$s $G
done
$S/variant.sh $S/exact-abl3 eR0 rank=0 $G
echo abl5 done

#!/bin/bash
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
$S/variant.sh $S/exact-master2 master2 - 1000 1040 1196 1771 2030 2044 1309 1508 1920
echo base2 done

#!/bin/bash
# usage: ab.sh LABEL_A BIN_A LABEL_B BIN_B GAME...   alternating, one game at a time, one thread
S=${STUDY_DIR:-$(cd "$(dirname "$0")" && pwd)}
la=$1; ba=$2; lb=$3; bb=$4; shift 4
for n in "$@"; do
  $S/variant.sh $ba $la - $n > /dev/null
  $S/variant.sh $bb $lb - $n > /dev/null
done
echo ab done

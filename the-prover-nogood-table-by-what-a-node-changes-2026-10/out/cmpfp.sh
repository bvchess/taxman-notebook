#!/bin/bash
# cmpfp.sh A B: compare two fingerprint outputs, ignoring the seconds.
diff <(sed -E 's/ secs=[0-9.]+ ms\/node=[0-9.]+//' $1) <(sed -E 's/ secs=[0-9.]+ ms\/node=[0-9.]+//' $2) && echo SAME

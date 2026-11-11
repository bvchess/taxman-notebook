#!/bin/bash
# ./run.sh TAG N SCORE [FLAG...]: one search of game N from the floor SCORE (`taxman floor N SCORE`) with the build
# taxman-floor beside this script, on 16 threads at nice 19, its checkpoint and clock in ckpt/TAG, its stdout in
# out/TAG.txt and its stderr (the progress lines) in log/TAG.log.  jobs.log gets a line when it starts and ends,
# Pacific time.  The same command resumes a search that a limit or a signal stopped.
set -u
here=/home/brian/taxman_work/lab/work/floor
tag=$1
n=$2
score=$3
shift 3
mkdir -p "$here/out" "$here/log" "$here/ckpt"
stamp() { TZ=America/Los_Angeles date '+%F %T %Z'; }
echo "$(stamp) start $tag: floor $n $score $*" >> "$here/jobs.log"
nice -n 19 "$here/taxman-floor" floor "$n" "$score" --threads 16 --checkpoint-dir "$here/ckpt/$tag" "$@" \
    >> "$here/out/$tag.txt" 2>> "$here/log/$tag.log"
status=$?
echo "$(stamp) end $tag: exit $status" >> "$here/jobs.log"
exit $status

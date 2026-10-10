#!/bin/sh
# Same remaining PLAN2 jobs as run_rest_local.sh, split into three chains so they use the laptop's idle cores.
# Results don't depend on worker count (seeds are keyed on the item index). Finished jobs are skipped.
# usage: run_rest_parallel.sh F <pid-to-wait-for> | Ms | M
cd "$(dirname "$0")/.."
run() { .venv/bin/python code/run_screen.py "$1" "$2" 2>&1 | grep -v "WARNING\|internal variable\|^ \+[0-9.,-]\|^RESULT_B64"; }
case "$1" in
  F) while kill -0 "$2" 2>/dev/null; do sleep 20; done
     for j in ROB_F783T_w0.7 ROB_F783T_w1.3 ROB_F783T_10hz ROB_F783T_200hz; do run $j 4; done ;;
  Ms) for j in ROB_Ms_w0.7 ROB_Ms_w1.3 ROB_Ms_10hz ROB_Ms_200hz; do run $j 3; done ;;
  M) run 2A_M 3 ;;
esac
echo "CHAIN_DONE $1"

#!/bin/sh
# Remaining PLAN2 jobs on the laptop (free, resumable: finished jobs are skipped). Robustness first, then male default screen.
cd "$(dirname "$0")/.."
run() { .venv/bin/python code/run_screen.py "$1" "$2" 2>&1 | grep -v "WARNING\|internal variable\|^ \+[0-9.,-]\|^RESULT_B64"; }
for j in ROB_F783T_w0.7 ROB_F783T_w1.3 ROB_F783T_10hz ROB_F783T_200hz; do run $j 4; done
for j in ROB_Ms_w0.7 ROB_Ms_w1.3 ROB_Ms_10hz ROB_Ms_200hz; do run $j 3; done
run 2A_M 3
echo REST_DONE

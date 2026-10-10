#!/bin/sh
# Resumable PLAN2 chain (order fixed in PLAN2 Amendment 2, section E). Finished jobs are skipped.
cd "$(dirname "$0")/.."
run() { .venv/bin/python code/run_screen.py "$1" "$2" 2>&1 | grep -v "WARNING\|internal variable\|^ \+[0-9.,-]"; }
for j in 2B_F178 2B_M0.561 2B_M0.650 2B_M0.698 2B_M0.750 2B_M0.850 2C_Mbrain; do run $j 1; done
run SPEC_F 6; for j in SPEC_M1.000 SPEC_M0.561 SPEC_M0.698; do run $j 4; done
run 2A_F 6; run 2A_F783T 6
for j in 2A_Ms 2A_M698 2A_M; do run $j 4; done
for j in ROB_F783T_w0.7 ROB_F783T_w1.3 ROB_F783T_10hz ROB_F783T_200hz; do run $j 6; done
for j in ROB_Ms_w0.7 ROB_Ms_w1.3 ROB_Ms_10hz ROB_Ms_200hz; do run $j 4; done
echo CHAIN_DONE

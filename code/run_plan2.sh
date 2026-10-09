#!/bin/sh
# Resumable PLAN2 chain: finished jobs are skipped. Quick mechanism tests first, then the 106-type screens.
set -e
cd "$(dirname "$0")/.."
for j in 2B_F178 2B_M0.561 2B_M0.650 2B_M0.698 2B_M0.750 2B_M0.850 2C_Mbrain; do .venv/bin/python code/run_screen.py $j 1; done
.venv/bin/python code/run_screen.py 2A_F 6
.venv/bin/python code/run_screen.py 2A_M 4
.venv/bin/python code/run_screen.py 2A_Ms 4

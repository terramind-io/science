#!/bin/sh
# Cloud runner: rebuild every input from public sources (no large upload), then run PLAN2 jobs/shards.
# usage: sh code/cloud_run.sh NPROC "JOB[:i/n] JOB[:i/n] ..."
set -e
cd "$(dirname "$0")/.."
pip install -q "brian2==2.7.1" "numpy<2.1" pandas pyarrow joblib scipy "cython<3.1" openpyxl
mkdir -p vendor data/malecns data/flywire results/plan2
[ -d vendor/Drosophila_brain_model ] || { git clone -q https://github.com/philshiu/Drosophila_brain_model vendor/Drosophila_brain_model && git -C vendor/Drosophila_brain_model checkout -q 91bdd1e7dcf193f3e7ca5a8933497fcef63b7960; }
B=https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome
for f in body-annotations-male-cns-v1.0-minconf-0.5.feather body-neurotransmitters-male-cns-v1.0.feather connectome-weights-male-cns-v1.0-minconf-0.5.feather; do [ -f data/malecns/$f ] || curl -sSL -o data/malecns/$f $B/$f; done
(cd data/malecns && sha256sum -c ../../inputs/malecns_SHA256SUMS)
[ -f data/flywire/neuron_annotations.tsv ] || curl -sSL -o data/flywire/neuron_annotations.tsv https://raw.githubusercontent.com/flyconnectome/flywire_annotations/main/supplemental_files/Supplemental_file1_neuron_annotations.tsv
cp inputs/stimuli.json inputs/stimuli.locked.json
python code/prepare_inputs.py > /dev/null
cmp inputs/stimuli.json inputs/stimuli.locked.json && echo "inputs rebuilt identically"
for spec in $2; do j=${spec%%:*}; s=""; case "$spec" in *:*) s=${spec#*:};; esac; python code/run_screen.py $j $1 $s 2>&1 | grep -v "WARNING\|internal variable\|^ \+[0-9.,-]"; done

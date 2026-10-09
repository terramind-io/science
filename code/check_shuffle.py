"""Sanity check: the shuffle branch of run_sim.trial permutes signed weights across edges (multiset preserved)."""
import sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor' / 'Drosophila_brain_model')); sys.path.insert(0, str(ROOT / 'code'))
import run_sim
from model import create_model, default_params
comp, con = run_sim.DATA['flywire630']
neu, syn, spk = create_model(comp, con, dict(default_params))
w0 = np.asarray(syn.w[:]).copy()
w = np.asarray(syn.w[:])
perm = np.random.default_rng(20001).permutation(w)
syn.w[:] = perm * syn.w.unit if hasattr(syn.w, 'unit') else perm   # same expression as run_sim.trial
w1 = np.asarray(syn.w[:])
print('has_unit_attr', hasattr(syn.w, 'unit'))
print('n_edges', len(w0), 'fraction_changed', float(np.mean(w0 != w1)))
print('sorted_identical', bool(np.array_equal(np.sort(w0), np.sort(w1))))
print('sum_identical', bool(np.isclose(w0.sum(), w1.sum())), 'frac_negative', float((w0 < 0).mean()), float((w1 < 0).mean()))

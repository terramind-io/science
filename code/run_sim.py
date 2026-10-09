"""Run one pre-registered condition with Shiu et al. 2024's LIF model (vendor/model.py, unmodified).

Each trial builds the network from (completeness, connectivity), optionally permutes the signed
synaptic weights across existing edges (shuffle control; one fresh permutation per trial), drives
the stimulus neurons with Poisson input, and records every neuron's spike count.

usage: run_sim.py CONDITION   (conditions defined in CONDITIONS below)
"""
import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from joblib import Parallel, delayed

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor' / 'Drosophila_brain_model'))
from model import create_model, poi, default_params  # noqa: E402
from brian2 import Network, Hz, ms, seed as b2seed, prefs  # noqa: E402

V = ROOT / 'vendor' / 'Drosophila_brain_model'
I = ROOT / 'inputs'
S = json.load(open(I / 'stimuli.json'))
DATA = {
    'flywire630': (V / '2023_03_23_completeness_630_final.csv', V / '2023_03_23_connectivity_630_final.parquet'),
    'flywire783': (V / 'Completeness_783.csv', V / 'Connectivity_783.parquet'),
    'malecns': (I / 'malecns_completeness.csv', I / 'malecns_connectivity.parquet'),
}
# name: (dataset, stimulus ids, n_trials, shuffle)
CONDITIONS = {
    'E1_fw630_shiu_real':       ('flywire630', S['flywire630']['stim_shiu'], 30, False),
    'E2_fw630_shiu_shuffled':   ('flywire630', S['flywire630']['stim_shiu'], 100, True),
    'E3_fw783_typeset_real':    ('flywire783', S['flywire783']['stim_typeset'], 30, False),
    'E3_mcns_typesetL_real':    ('malecns', S['malecns']['stim_typeset_L'], 30, False),
    'E4_mcns_typesetL_shuffled': ('malecns', S['malecns']['stim_typeset_L'], 100, True),
    'S1_fw783_sugaronly_real':  ('flywire783', S['flywire783']['stim_sugaronly'], 30, False),
    'S1_mcns_sugaronlyL_real':  ('malecns', S['malecns']['stim_sugaronly_L'], 30, False),
    'S2_mcns_typesetR_real':    ('malecns', S['malecns']['stim_typeset_R'], 30, False),
    'BENCH_mcns_nostim':        ('malecns', [], 1, False),
}
RATE_HZ = 100


def trial(dataset, stim_ids, shuffle, t_seed, t_run_ms):
    prefs.codegen.target = 'cython'
    comp, con = DATA[dataset]
    params = dict(default_params)
    params['r_poi'] = RATE_HZ * Hz
    params['t_run'] = t_run_ms * ms
    b2seed(t_seed)
    neu, syn, spk = create_model(comp, con, params)
    if shuffle:
        w = np.asarray(syn.w[:])
        syn.w[:] = np.random.default_rng(t_seed).permutation(w) * syn.w.unit if hasattr(syn.w, 'unit') else np.random.default_rng(t_seed).permutation(w)
    ids = pd.read_csv(comp, index_col=0).index.values
    pos = {int(k): i for i, k in enumerate(ids)}
    pois, neu = poi(neu, [pos[int(x)] for x in stim_ids], [], params)
    net = Network(neu, syn, spk, *pois)
    net.run(params['t_run'])
    cnt = np.asarray(spk.count[:])
    nz = np.nonzero(cnt)[0]
    return pd.DataFrame({'neuron_id': ids[nz].astype('int64'), 'n_spikes': cnt[nz].astype('int32')})


def main(name, n_proc=7, t_run_ms=1000):
    dataset, stim, n, shuffle = CONDITIONS[name]
    out = ROOT / 'results' / f'{name}.parquet'
    t0 = time.time()
    seeds = [10_000 * (list(CONDITIONS).index(name) + 1) + k for k in range(n)]
    res = Parallel(n_jobs=n_proc)(delayed(trial)(dataset, stim, shuffle, s, t_run_ms) for s in seeds)
    df = pd.concat([r.assign(trial=k, seed=s) for k, (r, s) in enumerate(zip(res, seeds))], ignore_index=True)
    df['condition'] = name
    df.to_parquet(out)
    meta = {'condition': name, 'dataset': dataset, 'n_stim': len(stim), 'n_trials': n, 'shuffle': shuffle,
            'rate_hz': RATE_HZ, 't_run_ms': t_run_ms, 'wall_s': round(time.time() - t0, 1), 'seeds': seeds}
    json.dump(meta, open(out.with_suffix('.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in meta.items() if k != 'seeds'}))


if __name__ == '__main__':
    name = sys.argv[1]
    n_proc = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    t_run = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    main(name, n_proc, t_run)

"""PLAN5 amendment A: repeat the song runs in the reference implementation (Shiu et al.'s Brian2 model, unmodified), FlyWire v783.
usage: run_song_sim.py CONDITION NPROC  -> results/plan5/sim_{CONDITION}.json   (conditions: song, vpoEN, pC1; 30 one-second trials at 100 Hz)"""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from joblib import Parallel, delayed
ROOT = Path(__file__).resolve().parents[1]; V = ROOT / 'vendor' / 'Drosophila_brain_model'; sys.path.insert(0, str(V))
from model import create_model, poi, default_params  # noqa: E402
from brian2 import Network, Hz, ms, seed as b2seed, prefs  # noqa: E402
SETS = json.load(open(next(p for p in (ROOT / 'inputs/song_sets.json', ROOT / 'song_sets.json') if p.exists())))
COND = {'song': 'hearing', 'vpoEN': 'vpoEN', 'pC1': 'pC1'}; BASE = {'song': 510_000, 'vpoEN': 520_000, 'pC1': 530_000}; N_TRIALS = 30
def trial(stim, t_seed):
    prefs.codegen.target = 'cython'; p = dict(default_params); p['r_poi'] = 100 * Hz; p['t_run'] = 1000 * ms; b2seed(t_seed)
    comp, con = V / 'Completeness_783.csv', V / 'Connectivity_783.parquet'
    neu, syn, spk = create_model(comp, con, p); ids = pd.read_csv(comp, index_col=0).index.values; pos = {int(k): i for i, k in enumerate(ids)}
    pois, neu = poi(neu, [pos[i] for i in stim], [], p); net = Network(neu, syn, spk, *pois); net.run(p['t_run']); c = np.asarray(spk.count[:])
    st = set(pos[i] for i in stim)
    return {'seed': t_seed, 'vpoEN': [int(c[pos[i]]) for i in SETS['vpoEN']], 'vpoDN': [int(c[pos[i]]) for i in SETS['vpoDN']], 'pC1': [int(c[pos[i]]) for i in SETS['pC1']],
            'n_firing_nonstim': int(sum(1 for i in np.nonzero(c)[0] if i not in st))}
if __name__ == '__main__':
    name, nproc = sys.argv[1], int(sys.argv[2]); t0 = time.time(); stim = SETS[COND[name]]
    rows = Parallel(n_jobs=nproc)(delayed(trial)(stim, BASE[name] + k) for k in range(N_TRIALS))
    m = lambda key: float(np.mean([np.mean(r[key]) for r in rows]))
    out = {'condition': name, 'n_stim': len(stim), 'n_trials': N_TRIALS, 'rate_hz': 100, 'vpoEN_mean_hz': m('vpoEN'), 'vpoDN_mean_hz': m('vpoDN'), 'pC1_mean_hz': m('pC1'),
           'vpoDN_trials_with_any_spike': int(sum(1 for r in rows if sum(r['vpoDN']) > 0)), 'vpoEN_trials_with_any_spike': int(sum(1 for r in rows if sum(r['vpoEN']) > 0)),
           'n_firing_nonstim_mean': float(np.mean([r['n_firing_nonstim'] for r in rows])), 'wall_s': round(time.time() - t0, 1), 'trials': rows}
    o = ROOT / 'results/plan5'; o.mkdir(parents=True, exist_ok=True); json.dump(out, open(o / f'sim_{name}.json', 'w')); print(json.dumps({k: v for k, v in out.items() if k != 'trials'}))

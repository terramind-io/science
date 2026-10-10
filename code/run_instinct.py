"""PLAN4 part A: the simulation as an instinct function. Pre-registered in PLAN4.md.
usage: run_instinct.py real|shuffle|sens NPROC  -> results/plan4/instinct_{mode}.parquet"""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from joblib import Parallel, delayed
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor' / 'Drosophila_brain_model'))
from model import create_model, default_params  # noqa: E402
from brian2 import Network, PoissonGroup, Synapses, Hz, ms, seed as b2seed, prefs  # noqa: E402
V = ROOT / 'vendor' / 'Drosophila_brain_model'
COMP, CON = V / '2023_03_23_completeness_630_final.csv', V / '2023_03_23_connectivity_630_final.parquet'
XLS = ROOT.parent / 'sources/papers/S2_supplementary/S2_Shiu2024_MOESM2_ESM.xlsx'
OUT = ROOT / 'results' / 'plan4'; OUT.mkdir(parents=True, exist_ok=True)
READ = {'MN9': 720575940660219265, 'aBN1': 720575940630907434, 'aDN1': 720575940616185531, 'aDN2': 720575940629806974}

def senses():
    t4 = pd.read_excel(XLS, sheet_name='ST 4 Interaction betw Sugar, Wa', header=1); n4 = t4['Neuron Names'].astype(str)
    g = lambda p: [int(i) for i, nm in zip(t4['Flywire ID'], n4) if str(nm).startswith(p)]
    t7 = pd.read_excel(XLS, sheet_name='Supplemental Table 7A Grooming ', header=0); n7 = t7.iloc[:, 1].astype(str)
    j = lambda ps: [int(i) for i, nm in zip(t7.iloc[:, 0], n7) if any(str(nm).startswith(p) for p in ps)]
    return {'sweet': g('sugar'), 'bitter': g('bitter'), 'water': g('water'), 'Ir94e': g('Ir94e'), 'touch': j(['JO_']), 'touchCE': j(['JO_C', 'JO_E']), 'touchF': j(['JO_F'])}
# state: {sense: rate_hz}
PRIMARY = {'F1': {'sweet': 100}, 'F2': {'sweet': 100, 'bitter': 100}, 'F3': {'sweet': 100, 'Ir94e': 100}, 'F4': {'sweet': 200, 'bitter': 100}, 'F5': {'sweet': 200, 'Ir94e': 100},
           'F6': {'water': 100}, 'G1': {'touch': 100}, 'G2': {'touchCE': 100}, 'G3': {'touchF': 100},
           'U_nothing': {}, 'U_bitter': {'bitter': 100}, 'U_Ir94e': {'Ir94e': 100}, 'U_water_bitter': {'water': 100, 'bitter': 100}, 'U_sweet_water': {'sweet': 100, 'water': 100}, 'U_strong_sweet': {'sweet': 200}}
SENS = {**{f'S_sweet{a}_{s}{r}': {'sweet': a, s: r} for a in (100, 200) for s in ('bitter', 'Ir94e') for r in (50, 200)},
        'P_sugar': {'sweet': 62}, 'P_sugar_bitter': {'sweet': 62, 'bitter': 94}, 'P_sugar_Ir94e': {'sweet': 62, 'Ir94e': 116}, 'P_water': {'water': 216}, 'P_water_bitter': {'water': 216, 'bitter': 94}}
SHUF_CASES = ['F1', 'F5', 'F6', 'G1', 'G2']

def worker(jobs, n_trials, shuffle_seed, base_seed):
    prefs.codegen.target = 'cython'
    p = dict(default_params); S = senses()
    neu, syn, spk = create_model(COMP, CON, p)
    if shuffle_seed is not None:
        w = np.asarray(syn.w[:]); syn.w[:] = np.random.default_rng(shuffle_seed).permutation(w)
    ids = pd.read_csv(COMP, index_col=0).index.values.astype('int64'); pos = {int(k): i for i, k in enumerate(ids)}; N = len(ids)
    pg = PoissonGroup(N, rates=np.zeros(N) * Hz, name='stim')
    s_in = Synapses(pg, neu, on_pre='v += w_in', namespace={'w_in': p['w_syn'] * p['f_poi']}, name='stim_syn'); s_in.connect(j='i')
    net = Network(neu, syn, spk, pg, s_in); net.store('init'); rows = []
    for k, (name, state) in jobs:
        for t in range(n_trials):
            net.restore('init'); r = np.zeros(N); st = []
            for sense, hz in state.items():
                ix = [pos[i] for i in S[sense] if i in pos]; r[ix] = hz; st += ix
            pg.rates = r * Hz; rfc = np.full(N, float(p['t_rfc'] / ms)); rfc[st] = 0.0; neu.rfc = rfc * ms
            sd = base_seed + 1000 * k + t; b2seed(sd); net.run(p['t_run'])
            cnt = np.asarray(spk.count[:]); mask = np.ones(N, bool); mask[st] = False
            rows.append({'case': name, 'trial': t, 'seed': sd, 'shuffle_seed': shuffle_seed, 'n_stim': len(st), 'n_firing_nonstim': int((cnt[mask] > 0).sum()), **{nm: int(cnt[pos[i]]) for nm, i in READ.items()}})
    return rows

if __name__ == '__main__':
    mode, nproc = sys.argv[1], int(sys.argv[2]); t0 = time.time()
    if mode == 'shuffle':
        res = Parallel(n_jobs=nproc)(delayed(worker)([(k, (c, PRIMARY[c])) for k, c in enumerate(SHUF_CASES)], 3, 7000 + s, 40_000_000 + 100_000 * s) for s in range(10))
    else:
        cases = list((PRIMARY if mode == 'real' else SENS).items()); idx = list(enumerate(cases)); chunks = [idx[i::nproc] for i in range(nproc)]
        res = Parallel(n_jobs=nproc)(delayed(worker)(c, 30, None, 41_000_000 if mode == 'real' else 42_000_000) for c in chunks if c)
    df = pd.DataFrame([r for rr in res for r in rr]); df.to_parquet(OUT / f'instinct_{mode}.parquet')
    S = senses(); json.dump({'mode': mode, 'wall_s': round(time.time() - t0, 1), 'n_rows': len(df), 'sense_sizes': {k: len(v) for k, v in S.items()}}, open(OUT / f'instinct_{mode}.json', 'w'), indent=1)
    print(df.groupby('case')[list(READ)].mean().round(2).to_string()); print('wall', round(time.time() - t0, 1))

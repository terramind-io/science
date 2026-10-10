"""PLAN3 3A: how much of the feeding screen is readable from the wiring map alone? Pre-registered in PLAN3.md (commit abb98a0).
Writes results/plan3/3A.json and 3A_per_type.csv."""
import json, pickle, glob
from pathlib import Path
import numpy as np, pandas as pd
from scipy import sparse
from scipy.sparse.csgraph import shortest_path
from scipy.stats import mannwhitneyu
ROOT = Path(__file__).resolve().parents[1]; V = ROOT / 'vendor/Drosophila_brain_model'; P2D = ROOT / 'results/plan2'
OUT = ROOT / 'results/plan3'; OUT.mkdir(exist_ok=True)
SEZ = json.load(open(ROOT / 'inputs/sez_screen.json')); STIM = json.load(open(ROOT / 'inputs/stimuli.json'))
XLS = ROOT.parent / 'sources/papers/S2_supplementary/S2_Shiu2024_MOESM2_ESM.xlsx'
MN9F, MN9M = 720575940660219265, 10331

def load_map(comp, con):
    c = pd.read_csv(comp, index_col=0); e = pd.read_parquet(con)
    idx = {k: i for i, k in enumerate(c.index)}; n = len(idx)
    W = sparse.csr_matrix((e['Excitatory x Connectivity'].values.astype(float), (e['Postsynaptic_Index'].values, e['Presynaptic_Index'].values)), shape=(n, n))
    return idx, W
def auroc(s, l):
    s = np.asarray(s, float); l = np.asarray(l, bool)
    return float(mannwhitneyu(s[l], s[~l]).statistic / (l.sum() * (~l).sum()))
def path_score(W, idx, ids, target, hops=3, excit_only=False, cut=None):
    """Signed flow reaching `target` within `hops` steps, negatives clipped each step. `cut`: neuron indices whose output is removed."""
    Wm = W.maximum(0) if excit_only else W
    x = np.zeros(W.shape[0]); x[[idx[i] for i in ids if i in idx]] = 1; tot = 0.0
    for _ in range(hops):
        if cut is not None: x[cut] = 0
        x = np.maximum(Wm @ x, 0); tot += x[idx[target]]
    return tot
def hop_dist(W, idx, target):
    """Fewest steps from every neuron to target (each listed connection = one step)."""
    A = (W != 0).astype(np.int8).T.tocsr()  # A[pre, post]
    d = shortest_path(A.T.tocsr(), method='D', unweighted=True, indices=[idx[target]])[0]  # reversed graph from target
    return d
def sim_rates(job, col):
    fs = sorted(P2D.glob(f'{job}.parquet')) + sorted(P2D.glob(f'{job}__s*of*.parquet'))
    return pd.concat([pd.read_parquet(f) for f in fs]).groupby('item')[col].mean()
def boot(types, obs, a, b=None, n=10000, seed=0):
    rng = np.random.default_rng(seed); o = obs.values; A = a.values; B = None if b is None else b.values; out = []
    while len(out) < n:
        i = rng.integers(0, len(types), len(types))
        if o[i].all() or not o[i].any(): continue
        out.append(auroc(A[i], o[i]) - (0 if B is None else auroc(B[i], o[i])))
    return [round(float(np.percentile(out, 2.5)), 3), round(float(np.percentile(out, 97.5)), 3)]

def score_set(name, idx, W, key, target, sims):
    d = hop_dist(W, idx, target)
    types = sorted(k for k, v in SEZ.items() if len(v[key]) > 0 and all(k in s.index for s in sims.values()))
    obs = pd.Series([SEZ[k]['observed_rate'] > 0 for k in types], index=types)
    rows = {}
    for k in types:
        ids = [i for i in SEZ[k][key] if i in idx]
        dd = min([d[idx[i]] for i in ids]) if ids else np.inf
        rows[k] = {'observed_positive': bool(obs[k]), 'n_stim': len(ids), 'steps': None if np.isinf(dd) else int(dd),
                   'P2_path3': path_score(W, idx, ids, target), 'P2_path2': path_score(W, idx, ids, target, 2), 'P2_path4': path_score(W, idx, ids, target, 4),
                   'P2_excit3': path_score(W, idx, ids, target, 3, True), **{f'P3_{j}': float(s[k]) for j, s in sims.items()}}
    T = pd.DataFrame(rows).T; T['set'] = name
    P1 = -T['steps'].astype(float).fillna(99); P2 = T['P2_path3'].astype(float)
    res = {'n_types': len(types), 'n_positive': int(obs.sum()), 'always_no_accuracy': round(float((~obs).mean()), 3),
           'P1_steps': {'auroc': round(auroc(P1, obs), 3), 'ci95': boot(types, obs, P1)},
           'P2_path3': {'auroc': round(auroc(P2, obs), 3), 'ci95': boot(types, obs, P2), 'n_nonzero': int((P2 > 0).sum())},
           'sensitivity_only': {c: round(auroc(T[c].astype(float), obs), 3) for c in ['P2_path2', 'P2_path4', 'P2_excit3']},
           'steps_table': {str(k): [int(v), int(obs[T['steps'].fillna(99) == k].sum())] for k, v in T['steps'].fillna(99).value_counts().sort_index().items()}}
    for j in sims:
        S = T[f'P3_{j}'].astype(float); calls = S > 0
        res[f'P3_{j}'] = {'auroc': round(auroc(S, obs), 3), 'ci95': boot(types, obs, S), 'diff_P3_minus_P2': round(auroc(S, obs) - auroc(P2, obs), 3),
                          'diff_P3_minus_P2_ci95': boot(types, obs, S, P2), 'diff_P3_minus_P1': round(auroc(S, obs) - auroc(P1, obs), 3), 'diff_P3_minus_P1_ci95': boot(types, obs, S, P1),
                          'P2_vs_simulation_calls_auroc': round(auroc(P2, calls), 3) if calls.any() and not calls.all() else None, 'n_sim_positive': int(calls.sum())}
    return res, T

out = {}; tables = []
# --- development data (exploratory): v630, paper lists
idx630, W630 = load_map(glob.glob(str(V / '*ompleteness_630*.csv'))[0], glob.glob(str(V / '*onnectivity_630*.parquet'))[0])
st3 = pd.Series({k: v['st3_50hz_left'] for k, v in SEZ.items()})
out['DEV_v630_exploratory'], T = score_set('DEV_v630', idx630, W630, 'female_ids', MN9F, {'paperST3': st3}); tables.append(T)
x = pd.read_excel(XLS, sheet_name='Sup Table 3 Predicted MN9 vs. o', header=0); x = x[x.iloc[:, 1].notna()]
theirs = pd.Series(pd.to_numeric(x['Shortest Path'], errors='coerce').values, index=x.iloc[:, 0].astype(str).str.lower().values)  # names matched case-insensitively (corrected after the audit: 'Asteroid' was dropped)
ours = T['steps'].astype(float); ours.index = ours.index.str.lower()
OBSL = {k.lower(): v['observed_rate'] > 0 for k, v in SEZ.items()}
common = [k for k in ours.index if k in theirs.index]
same = int(((ours.reindex(common).fillna(99)) == (theirs.reindex(common).fillna(99))).sum())
out['P1_validity_vs_paper_column'] = {'n_types': len(common), 'exact_match': same, 'frac': round(same / len(common), 3),
                                      'mismatches': {k: [None if np.isnan(ours[k]) else int(ours[k]), None if np.isnan(theirs[k]) else int(theirs[k])] for k in common if (np.nan_to_num(ours[k], nan=99) != np.nan_to_num(theirs[k], nan=99))},
                                      'paper_column_auroc': round(auroc(-theirs.reindex(common).fillna(99), pd.Series([OBSL[k] for k in common], index=common)), 3)}
# exploratory, added after the audit: step count over connections of 5 or more synapses
e5 = pd.read_parquet(glob.glob(str(V / '*onnectivity_630*.parquet'))[0]); e5 = e5[e5['Connectivity'].abs() >= 5]
W5 = sparse.csr_matrix((np.ones(len(e5)), (e5['Postsynaptic_Index'].values, e5['Presynaptic_Index'].values)), shape=W630.shape)
d5 = hop_dist(W5, idx630, MN9F)
o5 = pd.Series({k.lower(): (lambda dd: np.nan if np.isinf(dd) else dd)(min([d5[idx630[i]] for i in v['female_ids'] if i in idx630], default=np.inf)) for k, v in SEZ.items()})
same5 = int((o5.reindex(common).fillna(99) == theirs.reindex(common).fillna(99)).sum())
out['P1_exploratory_5plus_synapses'] = {'n_types': len(common), 'exact_match_with_paper_column': same5, 'auroc': round(auroc(-o5.reindex(common).fillna(99), pd.Series([OBSL[k] for k in common], index=common)), 3)}
# --- C2: v783 typed lists
idx783, W783 = load_map(V / 'Completeness_783.csv', V / 'Connectivity_783.parquet')
out['C2_v783'], T = score_set('C2_v783', idx783, W783, 'female783_typed_ids', MN9F, {'2A_F783T': sim_rates('2A_F783T', 'ro_720575940660219265')}); tables.append(T)
# --- C1: male CNS
idxM, WM = load_map(ROOT / 'inputs/malecns_completeness.csv', ROOT / 'inputs/malecns_connectivity.parquet')
out['C1_male'], T = score_set('C1_male', idxM, WM, 'male_ids', MN9M, {j: sim_rates(j, 'ro_10331') for j in ['2A_Ms', '2A_M698', '2A_M']}); tables.append(T)
pd.concat(tables).to_csv(OUT / '3A_per_type.csv')

# --- C3: silencing (v630)
sez = pickle.load(open(V / 'sez_neurons.pickle', 'rb'))
def ids_of(name):
    for k in sez:
        if k.lower().replace('_', '').replace('-', '') == name.lower().replace('_', '').replace('-', ''): return list(sez[k]) if hasattr(sez[k], '__iter__') and not isinstance(sez[k], (int, np.integer)) else [sez[k]]
    return None
sugar = STIM['flywire630']['stim_shiu']
w6 = pd.read_excel(XLS, sheet_name='ST 6A Water Firing Rates', header=0)
water = [int(i) for i, nme in zip(w6.iloc[:, 0], w6.iloc[:, 1]) if str(nme).lower().startswith('water')]
c3_water_in_map = sum(i in idx630 for i in water)
C3 = {'sugar': {'stim': sugar, 'cases': {'Bract': False, 'Clavicle': True, 'Fdg': False, 'FMIn': True, 'G2N-1': True, 'Phantom': False, 'Rattle': True, 'Roundup': False, 'Usnea': True, 'Zorro': True},
                'sheet': 'Supplemental Table 2 Sugar Pred'},
      'water': {'stim': water, 'cases': {'Bract': True, 'Clavicle': True, 'G2N-1': False, 'Phantom': False, 'Rattle': True, 'Roundup': True, 'Tophat': False, 'Tulip': False, 'Usnea': True, 'Zorro': True},
                'sheet': 'Supplemental Table 5 Water Pred'}}
c3 = {'n_water_GRNs': len(water), 'n_water_GRNs_found_in_map': c3_water_in_map, 'n_sugar_GRNs': len(sugar), 'cases': [], 'excluded': []}
for cond, spec in C3.items():
    sh = pd.read_excel(XLS, sheet_name=spec['sheet'], header=0); ratio = dict(zip(sh.iloc[:, 0].astype(str), pd.to_numeric(sh.iloc[:, 6], errors='coerce')))
    for hops in (3, 4):
        base = path_score(W630, idx630, spec['stim'], MN9F, hops); c3[f'{cond}_baseline_P2_{hops}steps'] = float(base)
    for nm, req in spec['cases'].items():
        ids = ids_of(nm)
        if ids is None: c3['excluded'].append(f'{cond}:{nm} (not in sez_neurons.pickle)'); continue
        cut = [idx630[i] for i in ids if i in idx630]; row = {'condition': cond, 'cell_type': nm, 'required_in_real_flies': req, 'n_neurons': len(cut), 'sim_ratio_paper': float(ratio[nm]), 'sim_pred_required': bool(ratio[nm] < 0.8)}
        for hops in (3, 4):
            base = c3[f'{cond}_baseline_P2_{hops}steps']; r = path_score(W630, idx630, spec['stim'], MN9F, hops, cut=cut) / base if base > 0 else None
            row[f'map_ratio_{hops}steps'] = None if r is None else float(r); row[f'map_pred_required_{hops}steps'] = None if r is None else bool(r < 0.8)
        c3['cases'].append(row)
cs = pd.DataFrame(c3['cases'])
c3['n_cases'] = len(cs); c3['sim_correct'] = int((cs.sim_pred_required == cs.required_in_real_flies).sum())
for hops in (3, 4):
    col = f'map_pred_required_{hops}steps'; ok = cs[col].notna()
    c3[f'map_correct_{hops}steps'] = int((cs.loc[ok, col].astype(bool) == cs.loc[ok, 'required_in_real_flies']).sum()); c3[f'map_computable_{hops}steps'] = int(ok.sum())
out['C3_silencing'] = c3

# --- pre-registered verdicts
def m1(r, p): return r[p]['ci95'][0] > 0.5
c1, c2 = out['C1_male'], out['C2_v783']
d1, d2 = c1['P3_2A_Ms'], c2['P3_2A_F783T']
incl = lambda d: d['diff_P3_minus_P2_ci95'][0] <= 0 <= d['diff_P3_minus_P2_ci95'][1]
above = lambda d: d['diff_P3_minus_P2_ci95'][0] > 0
M2 = 'supported' if all(incl(d) and abs(d['diff_P3_minus_P2']) <= 0.10 for d in (d1, d2)) else ('not supported' if any(above(d) for d in (d1, d2)) else 'inconclusive')
k = 'map_correct_3steps' if c3['map_computable_3steps'] == c3['n_cases'] else None
M3 = 'not computable at 3 steps' if k is None else ('supported' if c3['sim_correct'] - c3[k] >= 3 else ('not supported' if c3[k] >= c3['sim_correct'] else 'inconclusive'))
out['verdicts'] = {'M1_P2': 'supported' if m1(c1, 'P2_path3') and m1(c2, 'P2_path3') else 'not supported', 'M1_P1_reported': 'supported' if m1(c1, 'P1_steps') and m1(c2, 'P1_steps') else 'not supported', 'M2': M2, 'M3': M3}
json.dump(out, open(OUT / '3A.json', 'w'), indent=1); print(json.dumps(out, indent=1))

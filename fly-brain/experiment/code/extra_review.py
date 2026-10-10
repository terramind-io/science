"""EXPLORATORY, added after the referee-style review of draft 2 (10 Oct 2026). Light array maths only; no simulation.
Writes results/plan3/3A_review_checks.json."""
import json, glob
from pathlib import Path
import numpy as np, pandas as pd
from scipy import sparse
from scipy.sparse.csgraph import shortest_path
from scipy.stats import mannwhitneyu
ROOT = Path(__file__).resolve().parents[1]; V = ROOT / 'vendor/Drosophila_brain_model'; R = ROOT / 'results/plan3'
T = pd.read_csv(R / '3A_per_type.csv', index_col=0); SEZ = json.load(open(ROOT / 'inputs/sez_screen.json')); A3 = json.load(open(R / '3A.json'))
def auroc(s, l):
    s = np.asarray(s, float); l = np.asarray(l, bool); return float(mannwhitneyu(s[l], s[~l]).statistic / (l.sum() * (~l).sum()))
def strat(o, a, b=None, n=10000, seed=0):
    rng = np.random.default_rng(seed); pos = np.where(o)[0]; neg = np.where(~o)[0]; v = []
    for _ in range(n):
        i = np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))]); v.append(auroc(a[i], o[i]) - (0 if b is None else auroc(b[i], o[i])))
    return [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)]
def plain_low(o, a, b, seed):
    rng = np.random.default_rng(seed); v = []
    while len(v) < 10000:
        i = rng.integers(0, len(o), len(o))
        if o[i].all() or not o[i].any(): continue
        v.append(auroc(a[i], o[i]) - auroc(b[i], o[i]))
    return round(float(np.percentile(v, 2.5)), 3)
out = {}
for name, simcol in (('C2_v783', 'P3_2A_F783T'), ('C1_male', 'P3_2A_Ms')):
    d = T[T['set'] == name]; o = d.observed_positive.astype(str).str.lower().eq('true').values; p2 = d.P2_path3.astype(float).values; p3 = d[simcol].astype(float).values
    lows = [plain_low(o, p3, p2, s) for s in range(12)]
    out[name] = {'P2_rank_test_p_one_sided': float(mannwhitneyu(p2[o], p2[~o], alternative='greater').pvalue), 'P3_rank_test_p_one_sided': float(mannwhitneyu(p3[o], p3[~o], alternative='greater').pvalue),
                 'stratified_ci': {'P2': strat(o, p2), 'P3': strat(o, p3), 'P3_minus_P2': strat(o, p3, p2)}, 'P3_minus_P2_lower_bound_seeds_0_11': [min(lows), max(lows)]}
    # label sensitivity: positive only if at least 20% of flies responded
    rate = np.array([SEZ[k]['observed_rate'] for k in d.index]); o2 = rate >= 0.2
    out[name]['positive_if_20pct_or_more'] = {'n_positive': int(o2.sum()), 'P2': round(auroc(p2, o2), 3), 'P3': round(auroc(p3, o2), 3)}
# silencing: both trivial baselines and a threshold-free ranking
c = pd.DataFrame(A3['C3_silencing']['cases']); req = c.required_in_real_flies.values.astype(bool)
out['silencing'] = {'n': len(c), 'n_required': int(req.sum()), 'always_required_correct': int(req.sum()), 'always_not_required_correct': int((~req).sum()),
                    'auroc_simulation_ratio': round(auroc(-c.sim_ratio_paper.values, req), 3), 'auroc_path_ratio_3steps': round(auroc(-c.map_ratio_3steps.values, req), 3)}
# thresholded map-only predictors (connections of 5 or more synapses) on every set
def load(comp, con):
    cc = pd.read_csv(comp, index_col=0); e = pd.read_parquet(con); return {int(k): i for i, k in enumerate(cc.index)}, e
def thr_scores(idx, e, key, target, types, thr=5):
    e = e[e['Connectivity'].abs() >= thr]; n = len(idx)
    W = sparse.csr_matrix((e['Excitatory x Connectivity'].values.astype(float), (e['Postsynaptic_Index'].values, e['Presynaptic_Index'].values)), shape=(n, n))
    Aadj = sparse.csr_matrix((np.ones(len(e)), (e['Postsynaptic_Index'].values, e['Presynaptic_Index'].values)), shape=(n, n))
    dist = shortest_path(Aadj, method='D', unweighted=True, indices=[idx[target]])[0]; ps, st = [], []
    for k in types:
        ids = [idx[i] for i in SEZ[k][key] if i in idx]; x = np.zeros(n); x[ids] = 1; tot = 0.0
        for _ in range(3): x = np.maximum(W @ x, 0); tot += x[idx[target]]
        ps.append(tot); dd = min(dist[ids]) if ids else np.inf; st.append(-(99 if np.isinf(dd) else dd))
    return np.array(ps), np.array(st)
sets = {'DEV_v630': (glob.glob(str(V / '*ompleteness_630*.csv'))[0], glob.glob(str(V / '*onnectivity_630*.parquet'))[0], 'female_ids', 720575940660219265, 'P3_paperST3'),
        'C2_v783': (V / 'Completeness_783.csv', V / 'Connectivity_783.parquet', 'female783_typed_ids', 720575940660219265, 'P3_2A_F783T'),
        'C1_male': (ROOT / 'inputs/malecns_completeness.csv', ROOT / 'inputs/malecns_connectivity.parquet', 'male_ids', 10331, 'P3_2A_Ms')}
out['thresholded_5plus_synapses'] = {}
for name, (comp, con, key, tgt, simcol) in sets.items():
    d = T[T['set'] == name]; o = d.observed_positive.astype(str).str.lower().eq('true').values; idx, e = load(comp, con)
    ps, st = thr_scores(idx, e, key, tgt, list(d.index)); p3 = d[simcol].astype(float).values
    out['thresholded_5plus_synapses'][name] = {'path_score': round(auroc(ps, o), 3), 'step_count': round(auroc(st, o), 3), 'n_nonzero_path': int((ps > 0).sum()), 'simulation': round(auroc(p3, o), 3),
                                               'sim_minus_thresholded_path_stratified_ci': strat(o, p3, ps)}
f1 = pd.read_parquet(ROOT / 'results/plan4/instinct_real.parquet'); g = f1[f1.case == 'F1'].MN9
out['own_sweet_100Hz_trials'] = {'n': int(len(g)), 'mean': round(float(g.mean()), 2), 'sd': round(float(g.std(ddof=1)), 2)}
json.dump(out, open(R / '3A_review_checks.json', 'w'), indent=1); print(json.dumps(out, indent=1))

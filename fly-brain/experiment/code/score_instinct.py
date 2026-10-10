"""Score PLAN4 part A (instinct function) by the pre-registered rules. Writes results/plan4/instinct.json."""
import json
from pathlib import Path
import pandas as pd, numpy as np
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / 'results' / 'plan4'
def load(mode):
    fs = sorted(P.glob(f'instinct_{mode}.parquet')) + sorted(P.glob(f'instinct_{mode}__s*of*.parquet'))
    return pd.concat([pd.read_parquet(f) for f in fs]) if fs else None
TRUTH = {'F1': ('extend', True), 'F2': ('extend', False), 'F3': ('extend', False), 'F4': ('extend', False), 'F5': ('extend', True), 'F6': ('extend', True),
         'G1': ('groom', True), 'G2': ('aBN1', True), 'G3': ('aBN1', False)}
def readout(g, kind):
    m = g[['MN9', 'aBN1', 'aDN1', 'aDN2']].mean()
    if kind == 'extend': return float(m.MN9), float((g.MN9 > 0).mean())
    if kind == 'aBN1': return float(m.aBN1), float((g.aBN1 > 0).mean())
    k = m[['aBN1', 'aDN1', 'aDN2']].idxmax(); return float(m[k]), float((g[k] > 0).mean())
out = {}; real = load('real')
assert real.groupby('case').size().eq(30).all() and not real.duplicated(['case', 'trial']).any()
cases = {}
for c, (kind, truth) in TRUTH.items():
    rate, frac = readout(real[real.case == c], kind)
    cases[c] = {'output': kind, 'real_flies': 'yes' if truth else 'no', 'mean_rate_hz': round(rate, 2), 'frac_trials_firing': round(frac, 2),
                'answer': 'yes' if rate >= 5 else 'no', 'match': (rate >= 5) == truth, 'answer_gt0': 'yes' if rate > 0 else 'no', 'answer_10hz': 'yes' if rate >= 10 else 'no'}
n = sum(v['match'] for v in cases.values())
out['cases'] = cases; out['I1'] = {'matched': n, 'of': len(cases), 'verdict': 'supported' if n >= 7 else ('not supported' if n <= 4 else 'inconclusive'),
                                   'matched_gt0': sum((v['answer_gt0'] == 'yes') == (v['real_flies'] == 'yes') for v in cases.values()),
                                   'matched_10hz': sum((v['answer_10hz'] == 'yes') == (v['real_flies'] == 'yes') for v in cases.values())}
out['unscored'] = {c: {'MN9_hz': round(float(g.MN9.mean()), 2), 'aBN1_hz': round(float(g.aBN1.mean()), 2), 'aDN1_hz': round(float(g.aDN1.mean()), 2), 'aDN2_hz': round(float(g.aDN2.mean()), 2)} for c, g in real.groupby('case') if c.startswith('U_')}
out['cross_checks'] = {'touch_read_at_extend_MN9_hz': round(float(real[real.case == 'G1'].MN9.mean()), 2), 'sweet_read_at_groom_max_hz': round(float(real[real.case == 'F1'][['aBN1', 'aDN1', 'aDN2']].mean().max()), 2)}
sh = load('shuffle')
if sh is not None:
    assert sh.groupby(['shuffle_seed', 'case']).size().eq(3).all()
    rows = []
    for (s, c), g in sh.groupby(['shuffle_seed', 'case']):
        rate, _ = readout(g, TRUTH[c][0]); rows.append({'scramble': int(s), 'case': c, 'rate': rate, 'yes': rate >= 5})
    S = pd.DataFrame(rows); f = float(S.yes.mean())
    out['I2'] = {'pairs': len(S), 'n_scrambles': int(S.scramble.nunique()), 'yes': int(S.yes.sum()), 'frac_yes': round(f, 3), 'max_rate_hz': round(float(S.rate.max()), 2),
                 'verdict': 'supported' if f < 0.10 else ('not supported' if f >= 0.5 else 'inconclusive'), 'mean_nonstim_neurons_firing': round(float(sh.n_firing_nonstim.mean()), 1)}
se = load('sens')
if se is not None:
    assert se.groupby('case').size().eq(30).all()
    out['sensitivity'] = {c: {'MN9_hz': round(float(g.MN9.mean()), 2), 'frac_trials_firing': round(float((g.MN9 > 0).mean()), 2)} for c, g in se.groupby('case')}
json.dump(out, open(P / 'instinct.json', 'w'), indent=1); print(json.dumps(out, indent=1))

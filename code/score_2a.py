"""Score PLAN2 2A jobs against Shiu et al. ST3 (observed optogenetic MN9 activation) per PLAN2 rules.
Merges shard files ({job}__s*of*.parquet). Writes results/plan2/score_2a.json."""
import json, glob
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import pearsonr
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / 'results' / 'plan2'
SEZ = json.load(open(ROOT / 'inputs' / 'sez_screen.json'))
READ = {'2A_F': 'ro_720575940660219265', '2A_F783T': 'ro_720575940660219265', '2A_M': 'ro_10331', '2A_Ms': 'ro_10331', '2A_M698': 'ro_10331'}
def load(job):
    files = sorted(P.glob(f'{job}.parquet')) + sorted(P.glob(f'{job}__s*of*.parquet'))
    if not files: return None
    d = pd.concat([pd.read_parquet(f) for f in files]); return d
def rates(job):
    d = load(job)
    if d is None: return None
    return d.groupby('item')[READ[job]].mean()  # mean spikes per 1 s trial = Hz
obs = pd.Series({k: v['observed_rate'] > 0 for k, v in SEZ.items()})
def metrics(pred, types, rng=np.random.default_rng(0)):
    p, o = pred.reindex(types).astype(bool).values, obs.reindex(types).values
    tp, fp = int((p & o).sum()), int((p & ~o).sum()); fn, tn = int((~p & o).sum()), int((~p & ~o).sum())
    acc = (tp + tn) / len(types)
    boots = [((p[i] == o[i]).mean()) for i in (rng.integers(0, len(types), len(types)) for _ in range(10000))]
    return {'n_types': len(types), 'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn, 'accuracy': round(acc, 3),
            'acc_ci95': [round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)],
            'trivial_all_negative_acc': round(float((~o).mean()), 3)}
out = {}
r = rates('2A_F')
if r is not None:
    st3 = pd.Series({k: v['st3_50hz_left'] for k, v in SEZ.items()})
    common = sorted(set(r.index) & set(st3.index))
    ours = r.reindex(common).fillna(0); theirs = st3.reindex(common)
    match = int(((ours > 0) == (theirs > 0)).sum())
    out['V0'] = {'n_types': len(common), 'classification_match': match, 'pearson_r': round(float(pearsonr(ours, theirs)[0]), 4),
                 'verdict': 'supported' if match >= 104 and pearsonr(ours, theirs)[0] >= 0.95 else 'not supported',
                 'scores_vs_observed': metrics(ours > 0, common),
                 'mismatches': {k: [round(float(ours[k]), 2), float(theirs[k])] for k in common if (ours[k] > 0) != (theirs[k] > 0)}}
ref = rates('2A_F783T')
for job, tag in [('2A_M', 'T1'), ('2A_Ms', 'T2'), ('2A_M698', 'T3')]:
    m = rates(job)
    if m is None or ref is None: continue
    common = sorted(set(m.index) & set(ref.index))
    f, mm = metrics(ref > 0, common), metrics(m > 0, common)
    kappa_agree = float(((ref.reindex(common) > 0) == (m.reindex(common) > 0)).mean())
    pos_mappable = int(obs.reindex(common).sum())
    sup = mm['accuracy'] >= f['accuracy'] - 0.05 and mm['TP'] >= 7
    nsup = mm['accuracy'] < f['accuracy'] - 0.15 or mm['TP'] <= 3
    out[tag] = {'job': job, 'female_783T': f, 'male': mm, 'agreement_with_female': round(kappa_agree, 3), 'observed_positive_mappable': pos_mappable,
                'verdict': 'supported' if sup else ('not supported' if nsup else 'partial')}
json.dump(out, open(P / 'score_2a.json', 'w'), indent=1)
print(json.dumps(out, indent=1))

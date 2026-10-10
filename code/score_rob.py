"""Score PLAN2 Amendment 2 robustness jobs (ROB_*) with the same rules as score_2a.py (T1/T2 thresholds).
For each condition the male (x0.561-based) run is judged against the female run of the same condition.
Writes results/plan2/score_rob.json."""
import json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; P = ROOT / 'results' / 'plan2'
SEZ = json.load(open(ROOT / 'inputs' / 'sez_screen.json'))
obs = pd.Series({k: v['observed_rate'] > 0 for k, v in SEZ.items()})
def rates(job, col):
    d = pd.read_parquet(P / f'{job}.parquet')
    assert not d.duplicated(['item', 'trial']).any()
    return d.groupby('item')[col].mean(), int(d.groupby('item').size().min()), int(d.groupby('item').size().max())
def metrics(pred, types, seed=0):
    rng = np.random.default_rng(seed)
    p, o = pred.reindex(types).astype(bool).values, obs.reindex(types).values
    tp, fp = int((p & o).sum()), int((p & ~o).sum()); fn, tn = int((~p & o).sum()), int((~p & ~o).sum())
    boots = [((p[i] == o[i]).mean()) for i in (rng.integers(0, len(types), len(types)) for _ in range(10000))]
    return {'n_types': len(types), 'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn, 'accuracy': round((tp + tn) / len(types), 3),
            'acc_ci95': [round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)],
            'positives': sorted(pred.reindex(types)[pred.reindex(types).astype(bool)].index)}
out = {}
for tag in ['w0.7', 'w1.3', '10hz', '200hz']:
    f, fmin, fmax = rates(f'ROB_F783T_{tag}', 'ro_720575940660219265')
    m, mmin, mmax = rates(f'ROB_Ms_{tag}', 'ro_10331')
    common = sorted(set(f.index) & set(m.index))
    ff, mm = metrics(f > 0, common), metrics(m > 0, common)
    sup = mm['accuracy'] >= ff['accuracy'] - 0.05 and mm['TP'] >= 7
    nsup = mm['accuracy'] < ff['accuracy'] - 0.15 or mm['TP'] <= 3
    out[tag] = {'trials_per_type': [fmin, fmax, mmin, mmax], 'female': ff, 'male': mm,
                'agreement': round(float(((f.reindex(common) > 0) == (m.reindex(common) > 0)).mean()), 3),
                'trivial_all_negative_acc': round(float((~obs.reindex(common)).mean()), 3),
                'T2_verdict': 'supported' if sup else ('not supported' if nsup else 'partial')}
verdicts = {k: v['T2_verdict'] for k, v in out.items()}
out['summary'] = {'verdicts': verdicts, 'T2_robust': len(set(verdicts.values())) == 1 and set(verdicts.values()) == {'supported'}}
json.dump(out, open(P / 'score_rob.json', 'w'), indent=1)
print(json.dumps(out, indent=1))

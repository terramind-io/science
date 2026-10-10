"""EXPLORATORY (not pre-registered), 10 Oct 2026. Lead only, not a finding.
Question: does simply following the wiring map a few steps from a cell type to MN9 predict the real-fly screen
(Shiu et al. 2024 Supplementary Table 3) about as well as the full simulation?
Score = summed signed-weight flow reaching MN9 within k steps (negative values clipped at each step), FlyWire v630,
the paper's own neuron lists. AUROC against observed positives (14 of 106) and against the paper's simulated calls.
Result on first run: k=3 gives AUROC 0.804 vs real flies (simulation's own rates: 0.853) and 0.983 vs the simulation's calls.
No confidence intervals, one dataset, 14 positives. Needs a pre-registered confirmation before it is used anywhere."""
import pandas as pd, numpy as np, json, glob
from pathlib import Path
from scipy import sparse
from scipy.stats import mannwhitneyu
ROOT = Path(__file__).resolve().parents[1]; V = str(ROOT / 'vendor/Drosophila_brain_model') + '/'
comp = pd.read_csv(glob.glob(V + '*ompleteness_630*.csv')[0], index_col=0)
con = pd.read_parquet(glob.glob(V + '*onnectivity_630*.parquet')[0])
idx = {k: i for i, k in enumerate(comp.index)}; n = len(idx)
W = sparse.csr_matrix((con['Excitatory x Connectivity'].values.astype(float), (con['Postsynaptic_Index'].values, con['Presynaptic_Index'].values)), shape=(n, n))
SEZ = json.load(open(ROOT / 'inputs/sez_screen.json')); mn9 = idx[720575940660219265]
names = sorted(SEZ); obs = np.array([SEZ[k]['observed_rate'] > 0 for k in names]); sim = np.array([SEZ[k]['st3_50hz_left'] for k in names])
def auroc(s, l): s = np.asarray(s, float); return mannwhitneyu(s[l], s[~l]).statistic / (l.sum() * (~l).sum())
out = {'simulation_vs_real': round(float(auroc(sim, obs)), 3), 'n_types': len(names), 'n_observed_positive': int(obs.sum())}
for hops in (1, 2, 3, 4):
    for mode, Wm in (('signed', W), ('excitatory_only', W.maximum(0))):
        sc = []
        for k in names:
            x = np.zeros(n); x[[idx[i] for i in SEZ[k]['female_ids'] if i in idx]] = 1; tot = 0.0
            for _ in range(hops): x = np.maximum(Wm @ x, 0); tot += x[mn9]
            sc.append(tot)
        out[f'{hops}hop_{mode}'] = {'auroc_vs_real': round(float(auroc(sc, obs)), 3), 'auroc_vs_simulation_calls': round(float(auroc(sc, sim > 0)), 3), 'n_nonzero': int((np.array(sc) > 0).sum())}
json.dump(out, open(ROOT / 'results/exploratory_pathcount.json', 'w'), indent=1); print(json.dumps(out, indent=1))

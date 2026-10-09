"""Fast runner for PLAN2. Each worker builds Shiu's network once (vendor/model.create_model, unmodified),
adds a PoissonGroup -> one-to-one Synapses(on_pre 'v += w_syn*f_poi') as the stimulus (same weight/target as
Shiu's PoissonInput), stores the initial state, and for each (item, trial) restores, sets rates + rfc=0 for
stimulated neurons, seeds and runs 1 s. Records readout spike counts and number of non-stimulated neurons firing.

usage: run_screen.py JOB  (JOBS below)
"""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from joblib import Parallel, delayed
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor' / 'Drosophila_brain_model'))
from model import create_model, default_params  # noqa: E402
from brian2 import Network, PoissonGroup, Synapses, Hz, ms, mV, seed as b2seed, prefs  # noqa: E402

V, I = ROOT / 'vendor' / 'Drosophila_brain_model', ROOT / 'inputs'
S = json.load(open(I / 'stimuli.json')); CTRL = json.load(open(I / 'controls.json')); SEZ = json.load(open(I / 'sez_screen.json'))
FW630 = (V / '2023_03_23_completeness_630_final.csv', V / '2023_03_23_connectivity_630_final.parquet')
FW783 = (V / 'Completeness_783.csv', V / 'Connectivity_783.parquet')
MCNS = (I / 'malecns_completeness.csv', I / 'malecns_connectivity.parquet')
MCNS_BRAIN = (I / 'malecns_brain_completeness.csv', I / 'malecns_brain_connectivity.parquet')
MN9_F = 720575940660219265; MN9_F_OTHER = 720575940645521262; MN9_ML, MN9_MR = 10331, 16949
DENS = 1 / 1.782
def sez_items(key):
    return [(k, v[key]) for k, v in SEZ.items() if v[key]]
# job: (data, items [(name, ids)], rate_hz, n_trials, wmul, readouts)
JOBS = {
    'V1_fw630_shiu21_100hz': (FW630, [('shiu21', S['flywire630']['stim_shiu'])], 100, 30, 1.0, [MN9_F, MN9_F_OTHER]),
    '2A_F': (FW630, sez_items('female_ids'), 50, 30, 1.0, [MN9_F, MN9_F_OTHER]),
    '2A_M': (MCNS, sez_items('male_ids'), 50, 30, 1.0, [MN9_ML, MN9_MR]),
    '2A_Ms': (MCNS, sez_items('male_ids'), 50, 30, DENS, [MN9_ML, MN9_MR]),
    '2B_F178': (FW783, [('typeset', S['flywire783']['stim_typeset'])], 100, 10, 1.782, [S['flywire783']['mn9_contra'], S['flywire783']['mn9_ipsi']]),
    **{f'2B_M{m:.3f}': (MCNS, [('typesetL', S['malecns']['stim_typeset_L'])], 100, 10, m, [MN9_ML, MN9_MR]) for m in (DENS, 0.65, 0.698, 0.75, 0.85)},
    '2A_F783T': (FW783, sez_items('female783_typed_ids'), 50, 30, 1.0, [MN9_F, 720575940618238523]),
    '2A_M698': (MCNS, sez_items('male_ids'), 50, 30, 0.698, [MN9_ML, MN9_MR]),
    'SPEC_F': (FW783, [(f'ctrl{k}', d) for k, d in enumerate(CTRL['female_draws'])], 100, 10, 1.0, [MN9_F, 720575940618238523]),
    **{f'SPEC_M{m:.3f}': (MCNS, [(f'ctrl{k}', d) for k, d in enumerate(CTRL['male_draws'])], 100, 10, m, [MN9_ML, MN9_MR]) for m in (1.0, DENS, 0.698)},
    **{f'ROB_F783T_{tag}': (FW783, sez_items('female783_typed_ids'), hz, 10, w, [MN9_F, 720575940618238523]) for tag, hz, w in (('w0.7', 50, 0.7), ('w1.3', 50, 1.3), ('10hz', 10, 1.0), ('200hz', 200, 1.0))},
    **{f'ROB_Ms_{tag}': (MCNS, sez_items('male_ids'), hz, 10, DENS * w, [MN9_ML, MN9_MR]) for tag, hz, w in (('w0.7', 50, 0.7), ('w1.3', 50, 1.3), ('10hz', 10, 1.0), ('200hz', 200, 1.0))},
    '2C_Mbrain': (MCNS_BRAIN, [('typesetL', S['malecns']['stim_typeset_L'])], 100, 10, 1.0, [MN9_ML, MN9_MR]),
}

def worker(data, chunk, rate_hz, n_trials, wmul, readouts, job_idx):
    prefs.codegen.target = 'cython'
    comp, con = data
    p = dict(default_params); p['w_syn'] = p['w_syn'] * wmul
    neu, syn, spk = create_model(comp, con, p)
    ids = pd.read_csv(comp, index_col=0).index.values.astype('int64'); pos = {int(k): i for i, k in enumerate(ids)}
    N = len(ids)
    pg = PoissonGroup(N, rates=np.zeros(N) * Hz, name='stim')
    s_in = Synapses(pg, neu, on_pre='v += w_in', namespace={'w_in': p['w_syn'] * p['f_poi']}, name='stim_syn')
    s_in.connect(j='i')
    net = Network(neu, syn, spk, pg, s_in)
    net.store('init')
    ro = [pos[r] for r in readouts if r in pos]
    rows = []
    for item_idx, (name, stim) in chunk:
        st = [pos[int(x)] for x in stim if int(x) in pos]
        for t in range(n_trials):
            net.restore('init')
            r = np.zeros(N); r[st] = rate_hz; pg.rates = r * Hz
            rfc = np.full(N, float(p['t_rfc'] / ms)); rfc[st] = 0.0; neu.rfc = rfc * ms
            sd = 1_000_000 * (job_idx + 1) + 1000 * item_idx + t
            b2seed(sd)
            net.run(p['t_run'])
            cnt = np.asarray(spk.count[:]); mask = np.ones(N, bool); mask[st] = False
            rows.append({'item': name, 'trial': t, 'seed': sd, 'n_stim': len(st),
                         'n_firing_nonstim': int((cnt[mask] > 0).sum()), 'spikes_nonstim': int(cnt[mask].sum()),
                         **{f'ro_{readouts[k]}': int(cnt[ro[k]]) for k in range(len(ro))}})
    return rows

def main(job, n_proc):
    if (ROOT / 'results' / 'plan2' / f'{job}.json').exists():
        print(json.dumps({'job': job, 'skipped': 'already done'})); return
    data, items, rate, n, wmul, readouts = JOBS[job]
    t0 = time.time()
    idx_items = list(enumerate(items))
    chunks = [idx_items[k::n_proc] for k in range(n_proc)]
    res = Parallel(n_jobs=n_proc)(delayed(worker)(data, c, rate, n, wmul, readouts, list(JOBS).index(job)) for c in chunks if c)
    df = pd.DataFrame([r for rr in res for r in rr]); df['job'] = job
    out = ROOT / 'results' / 'plan2' / f'{job}.parquet'; out.parent.mkdir(exist_ok=True); df.to_parquet(out)
    meta = {'job': job, 'n_items': len(items), 'rate_hz': rate, 'n_trials': n, 'w_syn_multiplier': wmul, 'readouts': readouts,
            'wall_s': round(time.time() - t0, 1)}
    json.dump(meta, open(out.with_suffix('.json'), 'w'), indent=1); print(json.dumps(meta))

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 6)

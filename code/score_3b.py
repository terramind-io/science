"""PLAN3 3B: reconcile the two independent extractions and score R1-R3. Writes census/resolved.csv and results/plan3/3B.json."""
import json, re
from pathlib import Path
import pandas as pd, numpy as np
ROOT = Path(__file__).resolve().parents[1]
a = pd.read_csv(ROOT / 'census/extract_A.csv', dtype=str).fillna(''); b = pd.read_csv(ROOT / 'census/extract_B.csv', dtype=str).fillna('')
m = a.merge(b, on='url', suffixes=('_A', '_B')); short = lambda u: u.split('github.com/')[1]
def first_num(s):
    x = re.search(r'-?\d+(?:[.,]\d+)?', s.replace('≥', '').replace('>=', '').replace('~', '').replace('≈', '')); return float(x.group().replace(',', '.')) if x else np.nan
# --- agreement between extractors (before any resolution)
inc_agree = int((m.include_A == m.include_B).sum()); both = m[(m.include_A == 'yes') & (m.include_B == 'yes')]
exact = int((both.mn9_hz_A.str.strip() == both.mn9_hz_B.str.strip()).sum())
norm = int(np.isclose(both.mn9_hz_A.map(first_num), both.mn9_hz_B.map(first_num), equal_nan=True).sum())
# --- resolutions by us, from the quoted lines (logged)
RES = {'ruiluohub/drosophila-lif-reproduction': ('no', 'only MN9 rates are for sugar plus bitter; not sugar-only'),
       'sikimsonikisler/sinek-beyni': ('no', 'only MN9 rate is for sugar plus bitter'),
       'NileshArnaiya/flybrain-RL': ('no', 'number is an expected value in a setup comment'),
       'lixiang1076/fly-brain': ('no', 'number appears only in a sample transcript'),
       'mertefesensoy/FlyBatch': ('no', 'the line with the number does not name MN9'),
       'cryptoghost1ng/Flymagotchi': ('no', 'the table with the number does not name MN9'),
       'danilo-lazovic/fly-bottlenecks': ('no', 'stimulus is a connectivity-selected taste set, not labelled sugar neurons')}
m['include'] = np.where(m.include_A == m.include_B, m.include_A, m.url.map(lambda u: RES.get(short(u), ('?',))[0]))
assert not (m.include == '?').any()
m['mn9'] = m.mn9_hz_A.map(first_num).where(m.mn9_hz_A != '', m.mn9_hz_B.map(first_num))
inc = m[m.include == 'yes'].copy()
conn = lambda r: r.connectome_A if r.connectome_A == r.connectome_B else f'{r.connectome_A} | {r.connectome_B}'
inc['connectome'] = inc.apply(conn, axis=1); inc['rate'] = inc.apply(lambda r: r.stim_rate_hz_A if r.stim_rate_hz_A == r.stim_rate_hz_B else f'{r.stim_rate_hz_A} | {r.stim_rate_hz_B}', axis=1)
out = {'frame': len(m), 'extractor_agreement': {'inclusion_same': inc_agree, 'of': len(m), 'both_included': len(both), 'mn9_exact_string_match': exact, 'mn9_first_value_match': norm},
       'resolutions': {k: {'include': v[0], 'reason': v[1]} for k, v in RES.items()}, 'included': len(inc), 'excluded': int((m.include == 'no').sum()),
       'connectome_counts_included': inc.connectome.value_counts().to_dict()}
# --- R1: headline case. Primary reading: both extractors say v630 and 100 Hz. Wider reading adds projects that compare their own number with the paper's shipped 67.0 Hz.
strict = inc[(inc.connectome == 'v630') & (inc.rate == '100')]
wide_extra = inc[~inc.index.isin(strict.index) & (inc.reference_hz_A.str.startswith('67.0') | inc.reference_hz_B.str.startswith('67.0'))]
def r1(d):
    ok = (d.mn9 - 67.0).abs() <= 5; n = len(d); f = ok.mean() if n else np.nan
    return {'n': n, 'within_5Hz': int(ok.sum()), 'frac': round(float(f), 3) if n else None, 'values': {short(u): v for u, v in zip(d.url, d.mn9)},
            'verdict': 'not assessable' if n < 5 else ('supported' if f >= 0.8 else ('not supported' if f < 0.5 else 'inconclusive'))}
out['R1_strict_v630_100Hz'] = r1(strict); out['R1_wide_adds_compares_with_67.0'] = r1(pd.concat([strict, wide_extra]))
# --- R2: shuffle / rewiring outcome for MN9 among included
sh = inc[(inc.shuffle_outcome_A.isin(['silent', 'reduced'])) | (inc.shuffle_outcome_B.isin(['silent', 'reduced'])) | inc.shuffle_outcome_A.str.startswith('other') & inc.shuffle_outcome_B.str.startswith('other')]
silent = sh[(sh.shuffle_outcome_A == 'silent') & (sh.shuffle_outcome_B == 'silent')]
f = len(silent) / len(sh) if len(sh) else np.nan
out['R2'] = {'n_reporting': len(sh), 'silent': len(silent), 'frac': round(f, 3), 'rows': {short(u): [x, y] for u, x, y in zip(sh.url, sh.shuffle_outcome_A, sh.shuffle_numbers_A)},
             'verdict': 'not assessable' if len(sh) < 5 else ('supported' if f >= 0.8 else ('not supported' if f < 0.5 else 'inconclusive'))}
# --- R3: male-map weight factor. A stated *correction*; an unchanged published weight (coded 1.0 by extractor A only) is not a correction and is listed separately.
def fac(r):
    for v in (r.male_weight_factor_B, r.male_weight_factor_A):
        try: return float(v)
        except ValueError: pass
    return np.nan
inc['male_factor'] = inc.apply(fac, axis=1)
unchanged = inc[(inc.male_weight_factor_A == '1.0') & (inc.male_weight_factor_B == 'not reported')]
corr = inc[inc.male_factor.notna() & ~inc.index.isin(unchanged.index)]
none_works = inc[(inc.male_weight_factor_A == 'none works') | (inc.male_weight_factor_B == 'none works')]
v = corr.male_factor; ratio = v.max() / v.min() if len(v) else np.nan
out['R3'] = {'n': len(v), 'values': {short(u): x for u, x in zip(corr.url, v)}, 'min': float(v.min()), 'max': float(v.max()), 'median': float(v.median()), 'max_over_min': round(float(ratio), 2),
             'n_between_0.5_and_0.65': int(((v >= 0.5) & (v <= 0.65)).sum()), 'stated_unchanged_weight_on_male_map': [short(u) for u in unchanged.url], 'state_no_single_factor_works': [short(u) for u in none_works.url],
             'verdict': 'not assessable' if len(v) < 4 else ('supported' if ratio >= 2 else ('not supported' if ratio <= 1.25 else 'inconclusive'))}
# --- settings reported by >= 3 included projects
inc['setting'] = inc.connectome + ' @ ' + inc.rate + ' Hz'
out['settings_with_3_or_more'] = {k: {'n': int(n), 'mn9_values': sorted(inc[inc.setting == k].mn9.dropna().tolist())} for k, n in inc.setting.value_counts().items() if n >= 3}
m[['url', 'include', 'include_A', 'include_B', 'connectome_A', 'connectome_B', 'stim_rate_hz_A', 'stim_rate_hz_B', 'mn9_hz_A', 'mn9_hz_B', 'reference_hz_A', 'shuffle_outcome_A', 'shuffle_outcome_B', 'male_weight_factor_A', 'male_weight_factor_B', 'quote_mn9_A', 'quote_shuffle_A', 'quote_male_A']].to_csv(ROOT / 'census/resolved.csv', index=False)
json.dump(out, open(ROOT / 'results/plan3/3B.json', 'w'), indent=1, ensure_ascii=False); print(json.dumps(out, indent=1, ensure_ascii=False))

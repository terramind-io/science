"""Rebuild results/plan2/<tag>.parquet (+ .json) from RESULT_B64 lines in a compute job log.
usage: recover_from_log.py LOGFILE [LOGFILE ...]   (skips tags that already exist locally)"""
import base64, gzip, io, json, sys
from pathlib import Path
import pandas as pd
P = Path(__file__).resolve().parents[1] / 'results' / 'plan2'
for log in sys.argv[1:]:
    metas = {}
    for line in open(log, errors='ignore'):
        line = line.strip()
        if line.startswith('{"job"'):
            try:
                m = json.loads(line); tag = m['job'] if not m.get('shard') else f"{m['job']}__s{m['shard'][0]}of{m['shard'][1]}"; metas[tag] = m
            except Exception: pass
        if line.startswith('RESULT_B64 '):
            _, tag, b64 = line.split(' ', 2)
            out = P / f'{tag}.parquet'
            if out.exists(): print('exists', tag); continue
            df = pd.read_csv(io.BytesIO(gzip.decompress(base64.b64decode(b64))))
            df.to_parquet(out)
            if tag in metas: json.dump(metas[tag], open(out.with_suffix('.json'), 'w'), indent=1)
            print('recovered', tag, len(df), 'rows')

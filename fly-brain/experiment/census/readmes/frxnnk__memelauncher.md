# BELLFLY — local experiment lab

Vault is no longer in this repository.

A published fly neural model produces spikes; a fixed decoder interprets them as LAUNCH_SIGNAL, NO_LAUNCH or INVALID. The model does not understand finance. **The live executor does not exist. No token was issued.**

This first delivery runs the original Shiu model on FlyWire v630, an explicitly synthetic MOCK integration runner, a persistent TypeScript controller, offline preview, export/verifier/replay and a read-only English React interface. Name, ticker, chain/platform selection and economics are provisional.

## Requirements and installation (Windows PowerShell)

Long / GOOGL preparation is isolated in [`integrations/long/README.md`](integrations/long/README.md). It has no signer or broadcast methods. The first diagnostic reverted because the reviewed factory was paused; this is not a successful provider preview. Historical neural manifests retain their original proposed terms.

Measured host: Windows, 16 logical CPU cores, about 61.7 GiB physical RAM; RTX 5060 Ti 16 GiB available but unused. The reference uses NumPy CPU with a measured peak around 2 GiB RAM. Allow ~3 GiB available RAM per concurrent reference run and sufficient disk for the virtual environment and ~86 MiB of model input data. Node **22.16.0** and Python **3.13.5** were used.

From this repository root:

```powershell
npm.cmd ci
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
python scripts/download-model.py
npm.cmd test
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_reference.py -v
npm.cmd run build
npm.cmd run demo
npm.cmd run dev
```

Open **http://127.0.0.1:8787**. Keep the server terminal running. `npm run dev` serves the built UI; after changing web files, build again. For Vite HMR, run `npm.cmd run web` in a separate terminal alongside the controller, then open port 5173. Both bind to loopback. No wallet/login/provider credential is required to watch or replay.

`npm.cmd` is intentional on Windows: a PowerShell npm wrapper dropped dash-prefixed arguments during initial tests. The reference control scripts below use fixed positional arguments. In other shells use `npm` and `.venv/bin/python` equivalents. Cross-platform numerical equality has not been tested.

Brian2 creates a CPU-feature cache under the OS user's `.brian` directory on first import, even when NumPy is selected. The Codex sandbox initially blocked that cache; a scoped first import outside the sandbox resolved it. Ordinary local use must allow that normal library cache. No existing credential file is needed.

## Actual model runs

```powershell
npm.cmd run reference
npm.cmd run reference:negative
npm.cmd run reference:ablated
```

- `reference`: the upstream sugarR example stimulus at 100 Hz, 21 published input IDs, one 1000 ms trial, MN9 output. All 127,400 rows in the supplied completeness table and 14,687,178 connectivity rows are loaded. A connectivity row is not the same thing as an individual anatomical synaptic contact.
- `reference:negative`: identical seed/duration/decoder with no stimulus.
- `reference:ablated`: identical stimulus with all incoming MN9 connection weights zeroed and independently checked. The final run records 229 affected connection rows.
- The seed is always **20260910**, declared as FIXED_LOCAL engineering work; it is not public randomness. Repeated development attempts are retained and documented, never presented as independent official trials.
- The decoder requires at least one MN9 spike in each of three consecutive 10 ms bins. This was fixed before the first reference and was not retuned to get a yes. It remains a provisional engineering policy, not a scientifically validated launch threshold.

Each command prints a run ID and writes its full evidence to `examples/<run-id>.json`. The controller's durable database is `.local/bellfly.sqlite`. Do not delete it to hide trials. `examples/reference-positive.json`, `reference-negative.json`, `reference-ablated.json` and `mock-demo.json` are named copies of the final delivery's records; the UUID records remain present. Consult [docs/RUN_LOG.md](docs/RUN_LOG.md) for failed and superseded engineering attempts.

## Verification and replay

```powershell
npm.cmd run verify -- examples/reference-positive.json
npm.cmd run replay -- examples/reference-positive.json
npm.cmd run verify -- examples/reference-negative.json
npm.cmd run verify -- examples/reference-ablated.json
npm.cmd run replay -- examples/mock-demo.json
```

`verify` checks the canonical export digest, manifest/artifact hashes, state/event history, complete clock/provenance, decoder recomputation and mock receipt boundaries. `replay` additionally checks current code/data/environment pins and reruns Python. It compares exact integer-microsecond spikes in the pinned local environment, with zero tolerance. It excludes wall time/RAM from numerical equality. Different hardware or original Brian2/Python may differ; no bitwise equivalence claim across those environments.

Changing runner/controller code, pinned dependencies or data intentionally blocks replay of the previous code hash. Older UUID examples are the engineering history, not promises to replay under modified code. Use the final named examples or the exact historical code snapshot if separately preserved. The current delivery has no earlier Git commits.

Canonical format `BELLFLY-C14N-1`: recursively sorted ASCII object keys, UTF-8 JSON, compact separators, finite JSON numbers, no undefined. The manifest digest is separate from the input object. `export_hash` is excluded from its own input. This restricted format is not a general RFC 8785 implementation. A local digest detects changes against a trusted reference; it cannot stop a hostile host replacing all evidence. There is no independently published timestamp or cryptographic execution proof.

## Safety and private control

`.env.example` documents defaults; the app does not automatically load `.env`. `LIVE_EXECUTION_ENABLED` must be unset or the string `false`. Any other setting refuses server startup. The manifest's field is a false literal, and `requestLive` always throws. There is no Bankr key lookup, wallet dependency, signed transaction builder or broadcasting path.

The public browser only reads `/api/runs`, individual records and `/evidence` downloads. There is no neural-event ingestion endpoint. Optional `POST /api/control/rehearsal` accepts only `{}`, launches a fixed MOCK rehearsal and requires a caller-supplied `BELLFLY_CONTROL_TOKEN` of at least 32 characters via bearer auth. This token is never provided to the public client or child runner. Without it HTTP control is disabled; the local CLI remains available. Do not reuse financial credentials for local control.

Offline adapter interface names `preview`, `request_once`, `reconcile`, `verify_receipt` are ours, not provider endpoints. Atomic SQLite reservation prevents duplicate simulated creation. Ambiguous attempts do not retry. MOCK receipts have no transaction hash, token/curve address or pool ID. A positive neural result is independent from deployment state, which remains disarmed.

The runner receives an environment allowlist and communicates over its private child stdout pipe. This is process separation, not an OS security boundary against a malicious same-user process. The live integration needs additional isolation, signer policy and remote reconciliation work; see [architecture](docs/ARCHITECTURE.md).

## What this proves and what it does not

The recorded reference, negative and ablation experiments demonstrate a local signal dependent on the stimulated circuit and its connection to the decoder. They do not establish biological consciousness, financial reasoning, a calibrated probabilistic rule, full reproduction of the paper's ensemble/figures, public autonomous execution, or any token value.

The original model's code is MIT. Dataset terms and the intended public use are separate questions; local work is not being stopped on a presumption of token sales. See [research](docs/RESEARCH.md), [source register](FUENTES.md), [competitors](competidores.json), [future official protocol](docs/PUBLIC_RUN_PROTOCOL.md), [issuance checklist](docs/FUTURE_ISSUANCE_CHECKLIST.md), [private launch/copy draft](docs/LAUNCH_DRAFT.md), and [NEXT_STEPS.md](NEXT_STEPS.md).

Dependencies are deliberately small: React for UI, Vite/TypeScript/tsx for building/running, Zod for strict boundaries, Node's SQLite for durable local state. Scientific packages and all transitive Python versions are pinned in `requirements.lock.txt`; model commit, licenses and exact input checksums are in `vendor/shiu.pin.json`.

<h1 align="center">
  <img src="site/favicon.svg" width="128" height="128" alt=""><br>
  FlyBatch
</h1>

<p align="center">
  <a href="https://github.com/mertefesensoy/FlyBatch/actions/workflows/ci.yml"><img src="https://github.com/mertefesensoy/FlyBatch/actions/workflows/ci.yml/badge.svg" alt="CI status" title="CI runs the checks that need no network file, and checks the 19 golden fingerprints, on GitHub's own gcc: a smoke test, not the determinism matrix (SRS VL-142)"></a>
  <a href="https://mertefesensoy.github.io/FlyBatch/"><img src="https://github.com/mertefesensoy/FlyBatch/actions/workflows/pages.yml/badge.svg" alt="Site deploy status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/mertefesensoy/FlyBatch" alt="Licence: MIT"></a>
  <a href="https://github.com/mertefesensoy/FlyBatch/releases"><img src="https://img.shields.io/github/v/release/mertefesensoy/FlyBatch?include_prereleases" alt="Latest release, pre-releases included"></a>
</p>

FlyBatch simulates the sugar-to-feeding circuit of the male fruit fly: a
501-neuron subcircuit taken from the MaleCNS v1.0 connectome, run with the
leaky integrate-and-fire model of Shiu et al. (2024) in a portable C89 engine
with a COBOL batch driver. On MVS, whose System/370 architecture has no IEEE
floating point, the engine does its IEEE 754 arithmetic in software (Berkeley
SoftFloat), and the nineteen golden requests give the same fingerprints on
every platform in the table below, from x86-64 to MVS 3.8j running under an
emulator.

> **FlyBatch has not run on IBM Z hardware. The project does not have IBM Z
> access yet.** Every MVS result in this repository comes from MVS 3.8j
> running under the Hercules emulator, and every s390x result from Linux
> running under QEMU, both on one x86-64 laptop. Nothing here has run on
> z/OS or on IBM CICS Transaction Server.

The specification, every decision and every verification limit are in
[`docs/ONFLY-SRS.md`](docs/ONFLY-SRS.md). A shorter account is
[`docs/overview.md`](docs/overview.md), and [`docs/README.md`](docs/README.md)
suggests where to start reading.

FlyBatch was called ONFLY until 2026-09-27 (SRS D-637). The engine and
the COBOL driver keep their MVS program names, ONFLYENG and ONFLYDRV,
the messages keep their ONF prefix, and the specification keeps its file
name, because those names are written into the job control, the
requirements and every recorded listing (D-638).

## What it looks like

![The 501-neuron subcircuit: somata and 10,783 connections, with MN9 and the sugar-sensing neurons marked](docs/media/srext-network.png)

The shipped subcircuit, drawn from its own network file and soma positions
by `tools/netpic.py`: 501 neurons, 10,783 connections, the two MN9 feeding
motor neurons as stars and the 14 sugar-sensing neurons as triangles. It
shows wiring, not activity; the live view below shows activity.

**How it works.** [`docs/architecture.md`](docs/architecture.md) explains the
system with diagrams: the data flow from the connectome to the three
platforms, the engine and its float layer, one timestep of the model, the
MVS job and the determinism matrix. [`docs/FAQ.md`](docs/FAQ.md) answers the
questions people ask first, and [`docs/writeup.md`](docs/writeup.md) tells
the story of the byte comparison and the compiler fault it found; every
paragraph in both cites the evidence it rests on.

**One golden request, three floating-point builds.** The same request, G-16,
through the native, SoftFloat 3e and SoftFloat 2c engines, each printing the
fingerprint the specification records for it:

![A terminal session: the engine run on G-16 with three floating-point builds, each printing FP=BAF81D91](docs/media/demo-linux.gif)

Recorded on Linux x86-64 under WSL with gcc 15.2.0, by asciinema and agg
from `tools/demo/demo.sh` (the replayable recording is
[`docs/media/demo-linux.cast`](docs/media/demo-linux.cast)). The same script
recorded by VHS on Windows with the recorded MinGW gcc 6.3.0 toolchain is
[`docs/media/demo-windows.gif`](docs/media/demo-windows.gif).

**The model running.** The live view draws spikes over the neurons' positions
while the engine streams them, here 60 ms of sugar at 40 Hz on x86-64:

![Spikes spreading through the subcircuit over 60 ms, with MN9 crossing threshold](docs/media/onfly-live-short.gif)

**On emulated MVS 3.8j.** The same request type answered through a 3270
transaction under INTERCOMM, a transaction monitor that is not CICS, and the
printed output of the batch job that computed it, both captured on
2026-09-27 from MVS 3.8j emulated by Hercules on a laptop:

![The 3270 screen's rows for G-17: FP=F9C7EE77 and both MN9 readouts](docs/media/mvs-3270-g17.png)

![The job's printed output for G-17: the engine's run manifest on MVS38J with SoftFloat 2c, and the report](docs/media/mvs-report-g17.png)

The emulated MVS job also streams its spikes to the host while it runs:
[`docs/media/onfly-mvs-live.gif`](docs/media/onfly-mvs-live.gif).

## Status

| Phase | What it covers | State |
|---|---|---|
| A | Environment, the SoftFloat port, transport, performance and COBOL spikes | Complete (D-252) |
| B | Engine and Python reference oracle on x86-64 | Complete (D-47) |
| C | Science on x86-64: calibration, subcircuit extraction, acceptance criteria | Complete (D-206) |
| D | Linux s390x under QEMU | Complete (D-234) |
| E | The MVS 3.8j batch job under Hercules, and the acceptance criteria ACC-1 to ACC-7 | Complete (D-348) |
| G | A transaction demonstrator: `EXEC CICS` source under a CICS-compatible runtime on Windows, a 3270 flow on the emulated MVS lab, and a live view | Complete (D-442) |
| F | z/OS | Not started: the project does not have IBM Z access yet |
| H | IBM CICS on z/OS | Not started; depends on F |

The phase letters are labels, not an order; the order was A, B, C, D, E, G,
then F and H.

Determinism, the golden fingerprints of the nineteen Section 8.4 requests
(SRS Section 8.3):

| Row | Platform | Floating point | Compiler | Requests matching |
|---|---|---|---|---|
| 1 | x86-64 | Python reference | none | 19 of 19 |
| 2 | x86-64 | native | MinGW gcc 6.3.0 | 19 of 19 |
| 3 | x86-64 | SoftFloat 3e | MinGW gcc 6.3.0 | 19 of 19 |
| 3b | x86-64 | SoftFloat 2c | MinGW gcc 6.3.0 | 19 of 19 |
| 4 | Linux s390x under QEMU | SoftFloat 3e | gcc 13.3.0 | 19 of 19 |
| 5 | Linux s390x under QEMU | native | gcc 13.3.0 | 19 of 19 |
| 6 | MVS 3.8j under Hercules | SoftFloat 2c | GCCMVS 3.2.3 | 19 of 19 |
| 7 | MVS 3.8j under Hercules | SoftFloat 2c | JCC 1.50.00 | 19 of 19 |
| 8 | z/OS | | | empty |

On MVS the response records are identical to the x86-64 ones byte for byte
apart from one text field that MVS stores in EBCDIC. Identical fingerprints
show that the platforms agree with each other; they do not show that any of
them is correct.

## What you can reproduce today

**1. Check the recorded evidence.** Needs Python 3 and the files in this
repository; it compares recordings, it does not re-run them.

```
python tests/run_tx.py --compare data/phase-d/x86w data/phase-d/s390x
python tests/run_mvsrun.py
python tests/run_mvsjcc.py
```

**2. Build and run the x86-64 suite.** The suite needs the two network
files, `srext` (171,768 bytes) and `path` (951,200 bytes), which are not in
git. They are published as assets of the release candidate `v0.5.1-rc.1`
for its testers, and will be of the first release, `v0.5.1` (SRS D-626,
D-634); their digests are in
[`data/networks/MANIFEST.json`](data/networks/MANIFEST.json).
[`REPLICATING.md`](REPLICATING.md) gives the commands to fetch, check and
place them and to run the suite on Windows with MinGW gcc 6.3.0 or on Linux
x86-64, and [`docs/testers.md`](docs/testers.md) is the same path as one
task.

**3. The emulated labs.** Linux s390x needs your own QEMU guest; the MVS rows
need your own TK5 system on Hercules and hours of emulated CPU. The 3270
demonstration cannot be reproduced from this repository at all, because the
transaction monitor it runs under, INTERCOMM, is under a non-commercial
licence and is kept out of this tree.

Tested platforms: x86-64 Windows 11 with 32-bit MinGW gcc 6.3.0; Linux x86-64
(Ubuntu 26.04 under WSL2, gcc 15.2.0; SRS VL-140); Linux s390x (Ubuntu 24.04,
gcc 13.3.0) under QEMU; MVS 3.8j under SDL Hercules 4.9.1 with GCCMVS and
JCC. macOS and arm64 are untested.

## Limits

* **The science was measured on x86-64 only.** On x86-64, sugar at 40, 60,
  120 and 200 Hz made the MN9 feeding motor neurons fire in all 30 seeds at
  every rate, and zero sugar produced zero spikes in all 501 neurons. MVS
  shows the fingerprints agree, not the science directly.
* **The subcircuit carries one fitted input term** standing in for the
  neurons it leaves out. With it, the 501-neuron subcircuit stays within 10%
  of the MN9 rate of the 184,099-neuron annotated MaleCNS network (39.0% of
  its synapses) at 40, 60, 120 and 200 Hz; 10 Hz is excluded because that
  network's rate is too variable there to test against. At 40 Hz the margin
  is smaller than the reference's own standard error, and a campaign
  re-measured with new seeds is estimated to pass 52 to 60% of the time.
* **Agreement with Shiu et al. is in shape, not magnitude.** Compared with
  their model of the female FlyWire connectome, re-run from their published
  code, FlyBatch's model on the annotated MaleCNS network rises with sugar in
  the same shape but fires more at low rates: 3.67 Hz at 10 Hz where the
  reference is silent, and 14.35 Hz against 4.73 Hz at 40 Hz. No single
  synaptic weight removes that gap.
* **Two acceptance criteria were changed after we saw the results:** ACC-3
  no longer tests 10 Hz, and ACC-4 no longer tests magnitude. Both changes
  and the failing numbers are recorded in the specification (D-202, D-340,
  D-341).
* **The s390x results come from Ubuntu 24.04 under QEMU's
  instruction-by-instruction emulation.** They show the code gives the same
  results on a big-endian system, and say nothing about floating point on
  real s390x hardware.
* **Performance figures are emulator figures.** Under Hercules 4.9.1 on an
  Intel Core i7-13650HX laptop, one standard 1000 ms request on the shipped
  network used 161 s of emulated CPU, inside the project's 10-minute budget.
  That is one run and says nothing about IBM Z performance.
* **The transaction is written in real `EXEC CICS` and runs on x86-64
  Windows under Raincode's CICS-compatible runtime, not under IBM CICS.** Its
  menu-screen program has never executed for lack of a licence, and running
  it concurrently is untested. On the emulated MVS lab, typing a request on a
  3270 session under INTERCOMM, a transaction monitor that is not CICS,
  starts a FlyBatch batch run and then shows its result and golden
  fingerprint.
* **The emulated MVS job streams its spike data to the host while it is
  still running**, and for the five shipped-network golden requests that
  stream is byte-identical to the x86-64 one once line endings are
  normalised. Comparing those streams line by line exposed a GCCMVS
  code-generation fault that had turned every +0.0 in the MVS kernel into a
  tiny subnormal, a difference no fingerprint had caught. It is worked
  around, and a 26-line reproducer shows its cause in the generated code:
  at -O1 an eight-byte structure of zeros is copied from a four-byte
  constant (SRS VL-145).

## Repository map

| Path | What it holds |
|---|---|
| `engine/` | The C89 engine, ONFLYENG |
| `cobol/` | The COBOL driver template, ONFLYDRV |
| `layout/`, `generated/` | The record layout's master definition and the files generated from it; generated files are committed because MVS has no Python |
| `softfloat/`, `third_party/` | The float layer and the vendored SoftFloat and TestFloat releases |
| `oracle/`, `prep/` | The Python reference kernel and the preparation pipeline |
| `reference/shiu/` | Shiu et al.'s model code and FlyBatch's re-run of their protocol |
| `cics/` | The `EXEC CICS` transaction source |
| `tests/`, `tools/` | The test suite, and the tools that build, submit and check the lab runs |
| `data/` | Recordings, measurements and manifests; see [`data/README.md`](data/README.md) |
| `docs/` | The specification, plans, implementation records and media |

## Licence

FlyBatch's own code is under the MIT licence in [`LICENSE`](LICENSE).
Third-party components and data are under their own terms, listed in
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md): SoftFloat 3e and TestFloat
3e (BSD), the Shiu et al. code (MIT), MaleCNS-derived data (CC BY 4.0, with
FlyBatch's own contribution also CC BY 4.0), and material derived from FlyWire
data (CC BY-NC 4.0, which does not reach the network files; SRS D-625).
`REUSE.toml` states the licence of every path.

**SoftFloat 2c is not BSD.** Every SOFT2C build, which means every MVS build
and part of the x86-64 test suite, contains Berkeley SoftFloat Release 2c,
whose terms restrict use to
those who accept all losses without recompense and who indemnify its author
and the International Computer Science Institute; read them in
`THIRD_PARTY_NOTICES.md` before you build it.

INTERCOMM, the monitor behind the 3270 demonstration, is under Tetragon LLC's
terms with a non-commercial clause and is not included.

## Trademarks

FlyBatch is a personal project by Mert Efe Şensoy. It is not an IBM product and
is not affiliated with, sponsored by or endorsed by IBM, or by any organisation
or person whose data, software or tools it uses, including HHMI Janelia, the
MRC Laboratory of Molecular Biology, the University of Cambridge, Google
Research, the FlyWire consortium, Raincode and the authors of Shiu et al.
(2024). IBM, IBM Z, z/OS, CICS and MVS are trademarks or registered trademarks
of International Business Machines Corporation, registered in many
jurisdictions worldwide; a current list is at
https://www.ibm.com/legal/copytrade. Linux® is the registered trademark of
Linus Torvalds in the U.S. and other countries. Other product and company
names, including Raincode, QIX and INTERCOMM, may be trademarks of their owners
and are used only to identify those products.

## How the project is built

FlyBatch is built with an AI coding agent, Anthropic's Claude Code, working
from the specification. The agent drafts code, tests and documentation and runs
the builds and the lab jobs. The owner makes every decision: each is recorded
with the alternatives offered in the specification's decision log (Appendix
A.1), and the agent's own proposals are kept apart (Appendix A.2) until the
owner decides them. A result is recorded only from a command actually run, with
its output, its platform and what it does not prove (Appendix D). Commits carry
the owner's name alone (D-478).

## Citing

Please cite FlyBatch as its citation file, [`CITATION.cff`](CITATION.cff),
gives it (GitHub shows it as "Cite this repository"), with the commit you used;
no release is archived yet. Cite the work it builds on too: the MaleCNS
connectome (Berg, S. et al., *Cell* 189:5504-5526.e15, 2026,
doi:10.1016/j.cell.2026.08.015) and the model (Shiu, P. K. et al., *Nature*
634:210-219, 2024).

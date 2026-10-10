# The fly brain

A wiring-only baseline for the whole-brain fruit fly simulation of Shiu et al. (2024, https://doi.org/10.1038/s41586-024-07763-9), and a survey of public re-runs of that model.

- Project page: https://terramind.org/fly-brain/
- Interactive lab: https://terramind.org/fly-brain/lab/
- Paper (release candidate, not peer-reviewed): [`paper/final/`](paper/final/)

## What is here

| Path | Contents |
|---|---|
| `experiment/` | Plans written before each run (`PLAN*.md`), code, inputs, result files and write-ups (`RESULTS*.md`). Its history is the original one; the paper cites its commit ids. |
| `experiment/census/` | The survey of public re-runs: the frozen list of repositories, both extraction passes and the resolved table. |
| `paper/` | Every version of the paper, the scripts that draw its figures and build the PDF, the fetched citation records, and the due-diligence log. |
| `JOURNEY.md` | A dated log of what we tried, what went wrong and what we changed. |

## Running it

Python 3.11. `experiment/code/prepare_inputs.py` and `experiment/code/cloud_run.sh` rebuild the inputs from public sources; the large connectome files are not stored here.

## Third-party data and code

- Model code: https://github.com/philshiu/Drosophila_brain_model (MIT).
- Male CNS connectome v1.0: https://male-cns.janelia.org (CC BY 4.0).
- FlyWire: flywire.ai states CC BY-NC 4.0; its Zenodo deposits state CC BY 4.0. This is a non-commercial project.

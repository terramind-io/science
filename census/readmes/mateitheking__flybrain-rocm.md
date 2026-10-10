# flybrain-rocm

Whole-brain spiking model of the fruit fly (*Drosophila*) running on **AMD
Radeon GPUs with ROCm on Windows**, plus a small 2D world where the simulated
brain steers a fly in closed loop.

The brain model is the leaky integrate-and-fire model of Shiu et al. (Nature
2024) on the FlyWire v783 connectome: 138 639 neurons, 15.1 M connections,
54.5 M synapses. The original code uses Brian2, and all ready-made GPU
simulators for it (Brian2CUDA, GeNN, NEST GPU) are CUDA-only. This repo has
its own engine: two HIP kernels compiled at runtime with hiprtc, no C++ build
step. It reproduces the original Brian2 model spike for spike.

Measured on an RX 7900 XTX, Windows 11, ROCm 7.2.1:

| engine | wall time per 1 s of fly life | vs real time |
|---|---|---|
| **GPU, RX 7900 XTX (this repo)** | **0.10 s** | **10x faster** |
| CPU, i5-14400F (this repo, numba) | 2.5 s | 0.4x |
| original Brian2 on the same PC | ~400 s | 0.0025x |

In the closed-loop arena (vision drives ~6 k neurons), the GPU version runs
~2x faster than real time and uses ~350 MB of VRAM.

## Quick start (Windows 11 + AMD Radeon)

Requirements: Python **3.12**, Adrenalin driver **26.2.2 or newer**, a GPU on
[AMD's Windows ROCm list](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/docs/compatibility/compatibilityrad/windows/windows_compatibility.html)
(tested: RX 7900 XTX, gfx1100). WSL is not needed.

```
git clone https://github.com/mateitheking/flybrain-rocm
cd flybrain-rocm
py -3.12 -m venv .venv-rocm
.venv-rocm\Scripts\python -m pip install -r requirements-rocm-windows.txt   # ~2.2 GB from repo.radeon.com
.venv-rocm\Scripts\python -c "import torch; print(torch.cuda.get_device_name(0))"
.venv-rocm\Scripts\python scripts\get_data.py                                # ~135 MB connectome + annotations
.venv-rocm\Scripts\python -m pytest tests                                    # includes the exact Brian2 check
.venv-rocm\Scripts\python run.py --scene loom                                # window; L / R launch a disc
```

Other commands:

```
python run.py --scene drum                 # rotating striped drum (optomotor response)
python run.py --scene mixed --headless --seconds 10
python run.py --engine cpu                 # force the CPU engine
python bench.py                            # speed of each engine
python -m experiments.escape              # escape statistics
python -m experiments.optomotor           # open-loop photoreceptor test (see Limits)
```

Without an AMD GPU: `pip install -r requirements.txt` and everything runs on
the CPU engine (about 0.13x real time in the arena).

## Windows ROCm pitfalls we hit (and how the code avoids them)

If you port other GPU code to ROCm on Windows, these may save you time:

- **Host <-> device copies from normal (pageable) memory take 15-25 ms each.**
  From pinned memory: ~9 us. `flybrain/gpu.py` only uses pinned buffers.
- **A kernel launch costs ~10 us** (~37 us through ctypes). The engine runs
  18 simulation steps per launch.
- **`torch.sparse_csr` matmul took 19 ms** for this 15 M-entry matrix, about
  100x slower than expected, so it is not used.
- **The Python interpreter hangs for minutes at exit** after using the GPU.
  Scripts and the test suite exit with `os._exit` (`run.exit_now`,
  `tests/conftest.py`).
- **No PyTorch C++ extension build needed:** `flybrain/hip.py` compiles HIP
  source with the hiprtc DLL that PyTorch already loaded and launches it on
  torch tensors via `hipModuleLaunchKernel`.
- float64 `atomicAdd` seems to be comparatively slow on RDNA3; the spike
  fan-out is the biggest part of the GPU time.

## How the GPU engine works

The model's synaptic delay is 1.8 ms = 18 steps of 0.1 ms, so a spike cannot
affect anything during the next 18 steps. Per block of up to 18 steps:

1. `neurons` kernel: one thread per neuron runs all steps of the block
   (exact integration, threshold, synaptic input from a ring buffer, Poisson
   input, reset) and appends spikes to a list.
2. `fanout` kernel: 32 threads per spike add its outgoing weights into the
   ring-buffer slot that is delivered 18 steps later.

That is ~4 launches per 18 steps instead of hundreds.

## What is verified

- **Exactness:** with deterministic input (the Poisson probability is 1 every
  step), the GPU and CPU engines produce the same spike counts as the
  original Brian2 code for every neuron of the full network (12 809 spikes,
  0 differences); see `tests/`. With random input, firing rates correlate
  0.996-0.997 with Brian2 and differ by a median of 4 %.
- A detail that matters for reproducing Brian2: input that arrives while a
  neuron is refractory is lost. Accumulating it instead gives ~20 % higher
  rates.
- Known result from the paper: stimulating right-hemisphere sugar neurons
  makes the proboscis motor neuron MN9 fire (~80 Hz here).

## The fly in the arena

`envs/arena.py` is a round arena with a striped wall and dark discs.
`flybrain/vision.py` turns the fly's 1D panoramic view into input for the
optic lobes, and `flybrain/body.py` reads out descending neurons:

- turning: DNa01/DNa02 (right minus left)
- walking: DNp09 (P9) forward, MDN backward
- escape: DNp01 (Giant Fiber) -> jump

Closed-loop results:

- **Optomotor:** with the drum at +60 deg/s the fly turns +39..49 deg/s
  (gain 0.65-0.8); without the brain it does not turn.
- **Escape:** the Giant Fiber fires 0.19-0.27 s before contact in 6/6
  trials; closest approach 0.14-0.23 vs -0.01..0.02 without the brain.
  Turning away from the threat is not consistent.

## Limits (read before quoting results)

- **Light does not get through the lamina in this model.** Driving the
  photoreceptors makes L1/L2 fire weakly and T4/T5 stay silent (real L1-L3
  are graded, non-spiking neurons; LIF neurons cannot do that). So vision is
  computed in Python (a Reichardt motion detector and a looming detector)
  and injected at T4/T5 and LPLC2/LC4. Everything downstream of those
  (lobula plate -> HS/H2 -> DNa, LPLC2 -> Giant Fiber -> MDN) is the
  connectome.
- No learning or plasticity; weights come straight from the connectome.
- No spontaneous walking: forward speed has a constant base value.
- The gains and thresholds that map features to firing rates, and firing
  rates to movement (`vision.py`, `run.py`), are our choices, not biology.
- Linux ROCm is not tested. `hip.py` looks for the Linux library names, but
  that path has never run.

## Layout

```
flybrain/gpu.py        GPU engine (HIP kernels via hiprtc)
flybrain/hip.py        compile / launch HIP kernels on torch tensors
flybrain/cpu.py        CPU engine (numba, only visits active neurons)
flybrain/model.py      plain PyTorch version (slow, readable reference)
flybrain/reference.py  runs the original Brian2 code (optional, `pip install brian2`)
flybrain/data.py       connectome -> CSR (cached in data/csr_783.npz)
flybrain/vision.py     panorama -> T4/T5 and LPLC2/LC4 input
flybrain/body.py       photoreceptor and descending-neuron mapping
envs/arena.py          2D world;  run.py  closed loop + pygame window
tests/                 exact comparison with Brian2, MN9 result
```

## Credits and citations

- Model: Shiu, P.K. et al. *A Drosophila computational brain model reveals
  sensorimotor processing.* Nature (2024). Code: philshiu/Drosophila_brain_model (MIT).
- Connectome: Dorkenwald, S. et al. *Neuronal wiring diagram of an adult
  brain.* Nature (2024), and the FlyWire consortium.
- Annotations: Schlegel, P. et al. *Whole-brain annotation and multi-connectome
  cell typing of Drosophila.* Nature (2024).

The data is not included; `scripts/get_data.py` downloads it from the
original repositories. Please follow their terms and cite them.

Code in this repo: MIT.

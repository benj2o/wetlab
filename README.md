# Wetlab: experimental data for better AI scientists

We test whether training on experimental experience improves decisions on unfamiliar experimental problems. The first benchmark uses retrospective replay of measured genetic-perturbation screens.

- [Brief hypothesis, scoring rubric and experiment inventory](HANDOFF.md)
- [Experiment 1: assessment, protocol and commands](experiments/bda/README.md)
- [Execution estimate and experiment priorities](reports/2026-10-28-execution-and-priorities.md)
- [Colab CPU smoke test and setup notebook](notebooks/bda_start.ipynb)
- [Current results and interpretation](results/2026-10-28-software-verification/INTERPRETATION.md)

**Current evidence:** software verification on synthetic fixtures only. No biological performance, fine-tuning improvement or cross-study transfer result exists yet. Optional GPU paths are written, not runtime-verified.

Target remote: https://github.com/benj2o/wetlab.git. This local snapshot was prepared while shell DNS access to GitHub was unavailable. Remote contents/default branch and successful publication have not been verified. Do not overwrite existing remote history.

For each future experiment, commit the protocol, code, source/model revisions, dependency lock, seed/budget configuration, summary metrics and a short interpretation. Keep failures in the record. Use a dated result directory; mark synthetic and biological results clearly. Large raw data, checkpoints and private outcome tables should stay in durable artifact storage, referenced by checksums and a stable access-controlled location where necessary. No secrets or unrelated internal research notes are included here.

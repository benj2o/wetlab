# Software verification — 28 October 2026

**Evidence class: synthetic software test. No biological result.**

Eleven automated tests passed. They exercise hidden-outcome separation at the observation interface, outcome-order independence, fixed budgets, duplicate/out-of-library refusal, oracle scoring under feedback controls, deterministic replay, subprocess communication, duplicate-row validation, training export restrictions and paired-summary compatibility.

The external-process smoke campaign selected 24 of 40 invented candidates in three rounds of eight. It recovered nine of the 16 invented hits: precision 0.375, recall 0.5625 and enrichment 0.9375. These numbers are a deterministic engineering fixture; they provide no evidence about biological performance or an AI model. The external policy is a seeded random sampler.

Artifacts:

- `tests.txt`: complete verification output.
- `synthetic-campaign.json`: observations, selections, evaluator truth and per-round metrics for the invented fixture.
- `manifest.json`: code/fixture checksums and minimal environment metadata.

Public dataset retrieval failed in the authoring environment because GitHub DNS could not resolve. No public-screen agent run or weight training was performed. NumPy-based Linear-UCB and optional CUDA training/inference were not runtime-tested. The Colab notebook is authored but not executed there.

Next scientific milestone: audit and prepare real training-screen data, provision audited biological features, profile a compatible model, then complete true/shuffled/hidden feedback campaigns. Test screens stay untouched until choices are locked on validation.

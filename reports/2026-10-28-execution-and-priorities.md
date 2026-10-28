# Full execution estimate and priorities — 28 October 2026

Recommendation: authorize the whole scientific work package, but execute with early feasibility checks. Going straight to cloud compute saves local setup time; it does not remove data audit, context profiling or experimental design. No paid resources were started.

## Time estimate

These are planning estimates from workload arithmetic, not measured performance of this implementation. Assume one engineer/researcher, a single small open-weight base model, two LoRA arms, one main protocol, and access to a suitable GPU. Infrastructure/authentication delays are additional.

| Milestone | Estimated elapsed work |
|---|---|
| Data audit, assay objectives, fixed study split, feature provenance | 0.5–1.5 working days |
| GPU/dependency setup, token/memory profiling, valid output pilot, campaign/failure logging | 1–2 working days |
| Generate teacher trajectories; train histories and outcomes adapters | 0.5–2 working days, contingent on sequence length |
| Complete validation and locked held-out runs | 1–6 calendar days of compute at the illustrative rates below |
| Analyze failures, feedback controls, uncertainty and write interpretation | 0.5–1 working day |

Allow **5–10 working days end to end** for a first defensible full comparison. A 24–48 hour result is plausible for a small feasibility slice only. Budget **2–4 weeks** if full-library context is slow, memory forces rework, or additional training seeds are required. More GPUs reduce inference wall time, not the number of independent studies in the data.

The model evaluation workload is:

- 3 model arms × 3 feedback conditions × 3 evaluation assays (one validation + two held-out) × 20 campaign seeds × 5 rounds = **2,700 model decisions**.
- Of these, the final test portion alone is **1,800 decisions**.
- At 30 seconds per decision, evaluation is **22.5 GPU-hours**; at 3 minutes it is **135 GPU-hours**; at 10 minutes it is **450 GPU-hours**. These are conditional arithmetic scenarios, not speed predictions. Include prompt prefill, generated batch output and software overhead when measuring.
- Teacher trajectories on three training screens add 300 decisions for 20 seeds × five rounds. Alternative teacher configurations, failed runs, training, optimizer tuning and repeated training seeds add work beyond these totals.
- Campaign seeds are not training seeds. The initial matrix assumes one adapter per objective. Repeat promising effects with additional training seeds before a strong claim; this multiplies the trained-arm evaluations and training cost.

Benchmark 10 representative rounds and one forward/backward training step before forecasting cost. Use measured time and peak GPU memory, then compute cost as GPU-hours × the actual offered rate. No reliable dollar estimate exists until the model, context and hardware are selected.

## Colab decision

Colab can run the smoke test and help profile a model immediately. For the full sweep I prefer a persistent GPU VM with durable artifacts and resumable campaigns. Google states that GPU types vary; typical managed runtimes are at most 12 hours, while Pro+ can support up to 24 hours with enough compute units. Resource availability is not guaranteed. Dedicated resources have different limits. [Official FAQ](https://research.google.com/colaboratory/faq.html).

A Colab-branded notebook does not solve GPU-memory requirements. The current whole-genome library may exceed 32k tokens. The bundled trainer and agent refuse silent truncation. We still need to choose a tokenizer/model and measure actual prompt length. Long context may require a larger GPU or a revised interface; shortlisting candidates changes the experiment and must be declared and shared across arms.

Before any long run, add per-campaign durable writes and a resumable scheduler, plus periodic training checkpoints. The current trainer saves at completion and is not ready for an interruptible multi-session sweep. Use Drive/object storage for checkpoints and raw logs; GitHub for code, compact results, manifests and interpretations. The included notebook runs setup/verification, not unattended fine-tuning.

## Which other experiments are worth running?

### GB1: yes, a useful second setting

GB1 measures combinations at four amino-acid positions. FLIP offers mutation-distance splits (one/two/three versus rest), alongside a random split. Use a declared mutation/group split rather than relying on random neighbours. [FLIP documentation](https://github.com/J-SNACKKB/FLIP/tree/main/splits/gb1).

Run a sequential campaign with measured variants only, fixed assay budgets, equal initial observations and a strong sequence-based optimizer (one-hot ridge/ensemble or GP where practical). Report best discovered fitness, number above a prespecified threshold and the discovery curve. Compare training histories, outcome training and unchanged policy. Protein identity is constant: transfer to harder variants within GB1 is not transfer to a new protein or scientific domain. GB1 is a good way to debug the loop and test epistasis-sensitive acquisition; additional independent protein landscapes are needed for a broad protein-transfer claim. Estimated additional work after the harness is stable: **2–4 working days**, excluding a large multi-model training study.

### Anthropic binder data: yes, narrowly; stronger as an assay-reliability study

The release contains 1,440 designs across 16 targets with measurements from two vendors and links to raw traces. One target's measurements were inconclusive; the release reports binding assessments for 1,320 designs across the other 15 targets. Start with the small tables/docs tier, not all structures. [Dataset card](https://huggingface.co/datasets/Anthropic/claude-protein-binder-design).

The clean first question is whether pre-experiment computational features predict measured binding on held-out targets better after adaptation. Exclude all laboratory-result and final-assessment columns from the input, group related designs, and preserve censoring/missingness. Non-expressing, not-tested and failed-assay records are not automatically non-binders. Target/campaign/vendor effects need separate checks. Compare simple calibrated baselines before adding TabPFN fine-tuning. Better prediction would support a prediction product; it does not show better scientific decision-making.

A more interesting extension is assay interpretation: can the system distinguish credible binding from assay artifacts or vendor disagreement? Predeclare what evidence the agent receives and obtain an independently defensible reference assessment. The release's final two-vendor label cannot serve as an independent test if its constituent vendor measurements were already supplied as privileged input. This may point toward valuable data on negative results, controls and assay reliability, but that is a hypothesis to test, not a demonstrated buyer need.

Timebox initial tabular baseline and label audit to **1–2 working days**. Further feature/label engineering or fine-tuning can take longer. Stop if holdout performance is unstable or leakage dominates.

### Fresh wet-lab experiments: strongest eventual evidence, after a failure is named

Worth commissioning when a benchmark exposes a specific limitation and a prospective customer values fixing it. Buy training investigations and separate blinded evaluation investigations. The unit of value is a resolved capability gap, not simply the number of measurements. Cost and turnaround cannot be responsibly estimated before selecting the assay, throughput, controls and replication.

### GFP forecasting: defer

A technically clean forecast may still be commercially irrelevant to the better-scientist thesis. Revisit if a buyer wants drift detection, run-quality forecasting or laboratory monitoring. Do not spend physical budget to obtain an easy but strategically weak positive result.

CEO note: BDA is the most direct first test, GB1 is a useful robustness check, and the binder release is a cheap label/assay study. None alone establishes general scientific intelligence. The valuable result is a specific, reproducible capability improvement that a buyer recognizes.

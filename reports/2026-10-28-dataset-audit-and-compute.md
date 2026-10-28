# Protein and biological campaign audit, with compute plan

28 October 2026. This is a source-based feasibility assessment, not an executed biological benchmark. Sources reviewed: primary repository documentation, papers, archive listings, and selected CSV contents through web access. Full archives have not been downloaded or validated. The SAMPLE Zenodo landing page/API could not be retrieved; its paper and supplementary-data listings were accessible. Shell GitHub DNS remains unavailable. Scores are judgments of what to run next, relative to the better-AI-scientist thesis.

## Recommendation

Run ProteinGym as the main cross-study selection test (4/5). Use ALDE as a quick engineering/reproduction path (3/5), and metalloenzyme, SAMPLE and cell-free records as small, distinct real-campaign evaluations (3/5 for targeted tasks). SDLGuide is a useful same-day integration check (2/5). The combined campaign collection remains 3/5: heterogeneous data add useful stress tests, but do not automatically provide a clean cross-campaign policy benchmark.

AI-assisted setup should target hours, not weeks. A first executable run is different from a completed training comparison. An A6000 is ample for the small tabular and low-N optimizer components; compute is not the obstacle to those studies.

## Dataset assessments

### ProteinGym — 4/5, increase from 3

The reviewed repository lists 217 substitution DMS assays (~2.7 million measured variants), plus indel and clinical benchmarks. Use experimental DMS, not clinical pathogenicity classification, for the selection experiment. Its processed score direction is consistent (higher is better), but scale, biological meaning and wild-type relationship remain assay-specific. Multiple assays can share a protein. Source: [ProteinGym](https://github.com/OATML-Markslab/ProteinGym).

This is the strongest listed source for enough task diversity to train on some proteins and evaluate on untouched protein families. Construct replay histories by revealing measured outcomes round by round; call these reconstructed histories, not original scientific reasoning. Restrict proposals to measured variants. Group all assays of the same protein and related families into one split; sequence-identity clustering is useful but should be checked against domain/family annotations. Deduplicate GB1/TrpB or other reused landscapes across this and companion benchmarks.

Start with 20–40 diverse assays, after defining a family split across the full collection; select subsets by coverage/quality, not observed model gains. Use common seeds, fixed total budgets such as 32/64/128 measurements, and equal initial observations. Compare unchanged, outcomes-trained and history-trained models; include a frozen protein-model score, a supervised sequence model plus acquisition, and random. Tune on validation families. Audit external model scores for training-label contamination; published supervised predictions are not leakage-free test features simply because they can be downloaded.

Convincing result: a history-training advantage over both base and outcome training on held-out families, competitive with a tuned optimizer, with improvement dependent on true feedback. Report by family/protein, not pooled variant count. Report useful variants relative to a justified threshold and, where possible, wild type; top-decile variants are not necessarily improved proteins. This demonstrates retrospective selection transfer, not assay invention or unrestricted discovery.

### ALDE — 3/5 as a practical starting point; weaker as standalone transfer evidence

The code supports complete GB1 and TrpB simulation landscapes and a real ParPgb enzyme campaign. Crucially, the README says production-mode unmeasured entries are zero placeholders and production regret is meaningless. The processed ParPgb CSV exposes round membership and separate product/yield columns. Sources: [ALDE README](https://github.com/jsunn-y/ALDE), [campaign CSV](https://raw.githubusercontent.com/jsunn-y/ALDE/master/analysis/ParPgb_fitness_all.csv), [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11739421/).

Run its complete-landscape optimizer as a fast baseline/harness check. Do not count GB1 as a new independent setting if it was already used through FLIP or ProteinGym. Keep the actual ParPgb campaign separate: train on earlier rounds, predict/calibrate later measured outcomes and rank the actually tested next-round candidates. Keep yield and selectivity/objective definitions intact; collapse neither into an arbitrary scalar nor into missing=zero. Reconstruct batch history before seeing future results; strip row ordering that encodes yield.

A selection test over the union of observed ParPgb variants is possible, but is a restricted retrospective library test biased toward what the original experimenters selected. It cannot tell us what an arbitrary new proposal would have achieved. A fitted simulator supplies model predictions, not new experimental ground truth.

Convincing result: improved sample-efficient search on independent measured landscapes; improved next-round calibration or ranking in the real campaign is useful supporting evidence. One real enzyme campaign cannot establish general training transfer.

### SAMPLE — 3/5 for recovery, uncertainty and campaign interpretation

Four agents optimized the same GH1 landscape, each for 20 rounds of three proposals, initialized with six natural sequences. The study includes two erroneously accepted inactive-sequence measurements and reports roughly 9% experiment failures. Its unified landscape is a fitted GP, not a complete experimentally measured landscape. Source: [SAMPLE paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10926838/). The paper links the requested [Zenodo record](https://doi.org/10.5281/zenodo.10048592); that archive was not accessible in this review.

The valuable test is to distinguish evidence for an inactive enzyme from an inconclusive/failed experiment, then update predictions sensibly after contradictory results. Freeze observations at each historical round. Score next-round predictive calibration and data-quality flags against auditable experimental evidence, including later confirmation where available. Treat the two documented erroneous observations as case studies, not a statistically adequate diagnostic benchmark. If source traces permit additional independent cases, define them before model comparison.

For a restricted-library replay, deduplicate sequences across agents and retain independent replicate measurements/round timestamps. Holding one agent out tests a new trajectory on a shared biological task; it is not holding out a new protein family or study. Do not use a GP fitted to all agents as the experimental oracle or compare arbitrary counterfactual policies against it as if lab-validated.

Convincing result: better uncertainty handling and next-round judgments on a held-out campaign, followed by transfer testing on another study. This is closer to interpreting surprises than another noiseless hit-ranking table, but the evidence is small.

### Metalloenzyme active learning — 3/5, increase from 2

The study explores a five-position streptavidin design space of 3.2 million possible variants with thousands measured across rounds. The archive contains raw assay data and strategy-specific round files (e.g. informative, safe, hypothesis_testing), as well as separate embeddings/models/structures. Sources: [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11273458/), [assay archive listing](https://zenodo.org/records/12578395/preview/assay_and_ML_data.zip?include_deleted=0), [dataset](https://zenodo.org/records/12578395).

Start with the 365.5 kB assay archive, not 5 GB of structures or structure generation. The original work found cheap chemical descriptors adequate relative to more expensive features. Train on early rounds, predict the next measured batch, and test whether including the exploration round improves later ranking/calibration more than an equal-sized resampled earlier set. Match example count and account for differences in sampled regions; the historical acquisition policy creates selection bias, so do not call that contrast a randomized causal estimate.

Preserve replicates and plate/round provenance; never split replicate observations of one variant between training and test. Audit whether normalization or feature selection used later rounds. Saved all-data models and feature choices must not leak future labels into the baseline. Strategy names do not prove that original reasoning or action probabilities were logged.

Convincing result: transferable gains from noisy exploration data and uncertainty calibration on unseen campaign rounds. General acquisition-policy superiority still needs either a declared measured-only pool or fresh experiments. This is among the most relevant real-campaign datasets here.

### Cell-free biofoundry — 3/5 for formulation transfer

Three archives cover ColE1/proCFPS, ColM/proCFPS and ColM/euCFPS. Their listings include selected candidates, plate instructions and learner tables. The paper describes four optimization cycles; these are three related systems from one study. Sources: [dataset](https://zenodo.org/records/14904992), [archive listing](https://zenodo.org/records/14904992/preview/ColE1%20in%20proCFPS.zip?include_deleted=0), [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12529354/), [code](https://github.com/brsynth/icfree-ml).

Test transfer between formulation tasks: condition on component identities, concentrations/units, available ranges and assay context; expose only completed rounds and predict later measured recipes. Use calibrated ranking/error metrics and a GP or tree-ensemble baseline. Protein/system shift is a more informative holdout than random recipes; keep the results separate because output scales/readouts differ. Compare histories with equal-observation outcome-only training.

A directory of proposed recipes is not proof that every recipe has an experimental outcome. Link candidate IDs through liquid-handler instructions to actual measured learner tables. Distinguish readouts/proxies from direct protein yield and preserve controls. There is no established complete oracle over its enormous recipe space. A transfer result would support formulation-learning capability on related systems; it would not show arbitrary cross-domain scientist improvement.

### SDLGuide GOx assay — 2/5, keep as an integration check

The inspected tutorial CSV has 96 well rows, of which 40 have recorded iterations 1–5; other rows include measurements without iteration labels and empty placeholders. Columns include ABTS, HRP, GOx, glucose and slope. Source: [actual CSV](https://raw.githubusercontent.com/GormleyLab/SDLGuide/main/Hands-on%20Tutorial/GOx%20Assay%20data_bank_renamed.csv), [repository](https://github.com/GormleyLab/SDLGuide), [archive](https://zenodo.org/records/19190906).

Use it for a quick adapter test: parse completed measured experiments, resolve the meaning of Status and units from code/docs, preserve iterations, refuse missing outcomes and fit a simple baseline. Test on the next measured iteration or a declared measured-only pool. Repeated similar recipes and tiny sample size make random row splits particularly unpersuasive.

Convincing result: correct handling of a real assay campaign and possibly a small within-campaign predictive gain. It is not enough to support a data business or a general trained-scientist claim. The tutorial is useful precisely because it lets us verify the pipeline cheaply.

## Combined campaign design

Do not merge all values into one generic fitness column and call it five independent campaigns. Build a shared event schema: study, target/system, action features and units, round/timestamp, proposal/measurement/replicate identifiers, controls, observed result, uncertainty, validity and provenance. Preserve unmeasured actions as unknown, never zero/negative.

Two complementary evaluations:

1. **Closed-loop selection** on measured landscapes (ProteinGym, ALDE complete landscapes): score actual measured alternatives under a fixed budget.
2. **Historical campaign learning** on real rounds: score future measured observations and objective diagnostic judgments. Test leave-one-study-out where compatible and report every study separately. A recorded next choice is a behavior-imitation target, not proof that it was the best action.

Train on outcomes, histories, histories with order removed, and equal-token synthetic/reconstructed histories where appropriate. Use the same base weights and downstream tools. Original experimental decision histories are machine-acquisition records in several cases, not explanations from expert scientists. Establish that ordering adds value rather than just exposing more labels. Public-data/pretraining familiarity remains a limitation even with a perfect holdout split.

A combined result is interesting if benefits survive study holdout and measured-outcome evaluation. It does not become strong evidence merely because a fluent agent narrates five papers. Expensive RL cannot repair missing counterfactual labels.

## Reuse status

ProteinGym and ALDE repositories declare MIT; SDLGuide displays MIT. These are verified repository-level declarations, not a blanket conclusion about every raw-data component or separately hosted archive. The Zenodo pages rendered blank license fields in this inspection for several records; that does not establish that no license exists. SAMPLE's archive metadata could not be checked. Metalloenzyme/cell-free papers are accessible, but publication access is not a substitute for verifying archive/code terms. Resolve the exact artifact's terms before commercial redistribution or releasing trained artifacts. No third-party data have been copied into this repository.

## Hardware and timing

Assumption: RTX A6000 **48 GB** (Ampere), not another RTX 6000 model. [NVIDIA specifications](https://www.nvidia.com/en-us/products/workstations/rtx-a6000/).

An A6000 should handle low-N optimizers, cached protein embeddings and a modest 1–8B model with parameter-efficient tuning at controlled context lengths, subject to profiling. Full-library/full-sequence chat prompts are not required by the scientific question. Prefer a tool-accessible candidate catalogue and a defined search/ranking interface, held equal across arms; do not silently truncate or change available actions. The earlier BDA full-list prompt is an engineering choice to replace, not an inherent 80GB requirement of experimental selection.

Use 2–4 H100 80GB workers for the main sweeps after timing a representative run. Use H200/B200 when memory or a larger model justifies it; do not assume newer hardware is automatically cheaper per completed campaign. Use multi-GPU training only when a chosen model requires it. Independent studies/seeds usually parallelize more simply. Start with modest models; include a capable frozen frontier agent as a comparator if appropriate, while recognizing that the training comparison must use a trainable model with identical initial weights. A capable coding assistant is not evidence that the evaluated scientist policy has learned from the data.

The following are **unmeasured planning ranges**, not promises. First run means a cleaned-data baseline or narrow replay, not successful model training. GPU-hours assume one modest model, two training objectives, cached features, matched true/shuffled feedback, a limited search, and measured-only action interfaces. Small-campaign entries use historical prediction/diagnostic tests, not arbitrary-policy rollout. Classical-only runs can use far less GPU time. Shared training can reduce duplicated work; three training seeds, large RL sweeps and long-context models can increase it substantially.

| Experiment | First executable baseline, with agent-assisted setup | Initial comparison on one A6000, total GPU-hours | Initial result wall time on the A6000, including setup/analysis | Hardware guidance |
|---|---|---:|---|---|
| ProteinGym, 20–40 assay pilot | 0.5–1.5 days | 100–400 | 5–20 days | A6000 feasible; 2–4 H100 workers preferred for speed |
| ALDE complete-landscape check plus ParPgb analysis | 2–8 hours | 12–60 | 1–4 days | A6000; CPU baseline first |
| SAMPLE historical-round/recovery test | 4–12 hours after archive access | 12–60 | 1–4 days | A6000; CPU GP baseline |
| Metalloenzyme round transfer | 3–8 hours | 12–60 | 1–4 days | A6000; cheap descriptors first |
| Cell-free formulation transfer | 3–8 hours | 12–60 | 1–4 days | A6000; CPU tabular baseline |
| SDLGuide integration test | 1–3 hours | 0–4 | under one day | CPU; GPU optional |
| Combined leave-study-out campaign comparison | 1–2 days after adapters exist | 80–300 additional | 4–15 additional days | A6000 possible; parallel H100 workers useful |

A budgeted portfolio on 2–4 suitable cloud GPUs could produce first signals in 48–72 hours, a substantial first comparison in about a week, and a consolidated result in 2–3 weeks, conditional on archive access and compatible schemas. That is an execution target, not a measured hardware speedup. A full run over all ProteinGym assays and multiple training seeds is a later expansion, not included in the pilot row.

Workload anchor: 30 held-out assays × 10 campaign seeds × 5 rounds × 3 model arms × 2 feedback modes = **9,000 decisions**. At 20–90 seconds per decision that alone is 50–225 GPU-hours; timing depends on inference representation/model. Add feature extraction, teacher trajectories, fine-tuning and optimizer baselines. At three minutes per decision it becomes 450 GPU-hours. Use task/family-level intervals; extra campaign seeds do not create more biological studies.

## Budget

€100,000 is more than needed to answer the first questions; it is enough for a serious follow-up program. Do not turn available budget into a large parameter grid.

Official reference rates at review: Lambda lists a single A6000 at **$1.09/GPU-hour**, H100 PCIe 80GB at **$3.29**, H100 SXM 80GB at **$4.29**, and B200 180GB at **$6.99**, before applicable taxes. These are one-GPU instance listings, not cheaper multi-GPU-node per-chip quotes. Availability is unverified. [Provider pricing](https://lambda.ai/pricing).

For euro budgeting use a deliberately rounded **assumption of €5 per H100 GPU-hour all-in**, not a claimed currency conversion or provider quote. At that assumption, €100,000 buys 20,000 GPU-hours. Four H100s continuously for 14 days consume 1,344 GPU-hours, or €6,720; eight for 30 days consume 5,760 hours, or €28,800. Storage, API teachers, taxes and provider configurations can change costs; actual offers must replace this envelope.

Proposed first allocation, not authorization to spend:

- €5,000: data adapters, feature caching, profiling and baselines.
- €12,000: ProteinGym cross-family comparison and meaningful repeats.
- €5,000: real-campaign prediction/uncertainty/diagnostic tests.
- €8,000: larger-model check, matched-compute/synthetic-data controls and replication.
- €70,000 held for the most promising demonstrated effect or expanded independent task coverage.

Practical launch sequence: first day audit all small files and define measured-action support; days 2–3 run classical and frozen-policy pilots, while setting up a family split and cached features for ProteinGym; days 4–7 train the two data arms and execute locked tests; week 2 repeat promising results with additional training seeds and assemble interpretations. Do not wait for every archive or commercial-use question to resolve before doing independently usable engineering work.

CEO note: There is enough data here to get useful answers quickly. ProteinGym supplies breadth; the campaign records supply realism. The best outcome is a measurable gain from experimental experience on unfamiliar tasks. We should run toward that result, and refuse only the shortcuts that would make it uninterpretable.

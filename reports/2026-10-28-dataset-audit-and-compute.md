# Dataset audit and compute plan — 28 October 2026

This is a source/documentation audit and a proposed execution plan, not benchmark results or integrity-verified dataset downloads. Scores below judge usefulness for demonstrating that experimental data improves an AI scientist's capabilities. A narrower prediction or robotics business can justify different scores. No compute expenditure is authorized or incurred by this report.

## Decision

Make ProteinGym the principal broad selection benchmark; use HiTEA as an independent chemistry setting. Audit the real biological campaign bundle alongside them, because it is closest to learning from actual experimental histories. JUMP and Arc are good prediction experiments, but should be described and funded as such. Promote PRISM to a possible third selection setting and Autonomous Science Bench to an evaluation adjunct.

AI coding assistance should compress first runnable implementations to hours or a day for standard public tables. The remaining calendar time is predominantly data semantics, inference/training execution, repeated experiments and interpretation. One-shot code generation does not establish a valid split, supply missing counterfactual outcomes, or make a single campaign statistically independent of itself.

## The five originally scored 3

### 6. ProteinGym — raise to 4/5 for the first serious selection study

The repository advertises 217 substitution DMS assays and provides assay/protein metadata and processed measurements. Different assays can concern the same protein, and different proteins can be homologous. Freeze the actual release and count family/study groups after clustering; do not treat the advertised assay count as an independent-problem count. [Repository and schema](https://github.com/OATML-Markslab/ProteinGym), [reference metadata](https://github.com/OATML-Markslab/ProteinGym/blob/main/reference_files/DMS_substitutions.csv).

Proposed test: train a selection system on some protein families, validate on others, and reveal measurements sequentially on completely held-out families. Keep study, protein identity and homologous families together; select and document a clustering criterion before testing. Use only experimentally measured candidates as the replay action space. Run several small label budgets, for example 32, 96 and 192 measured variants where library size allows. Charge the common initial random observations to that budget.

Compare random; frozen zero-shot scoring; the strongest validation-tuned conventional acquisition baseline; outcome-trained models; and history-trained policies, keeping input representations and measurement exposure comparable. Test a specialist acquisition policy first and a fixed LLM scientist using that module separately. If only the specialist improves, the claim concerns that capability/module, not general reasoning by the LLM. If testing LLM weight adaptation, keep it as a separate matched-base-model comparison.

Primary endpoint: useful variants recovered per measured experiment; secondary endpoints: discovery curve and best fitness relative to an assay-specific reference. A within-assay top-decile threshold is acceptable for an algorithmic comparison but is not automatically a commercially useful improvement over wild type. Report functional categories separately and bootstrap over held-out family/study groups, not millions of variants or random campaign seeds. Predeclare an effect size meaningful in saved laboratory measurements.

The main limitation is outcome data rather than original decision history. We can generate selection histories and test learning from those; we cannot call them recorded experimental reasoning. This is nevertheless a clean, broad and useful first test of learned experimental selection. Use existing representations or cached permitted zero-shot scores initially; do not recompute every structure or fine-tune a giant protein foundation model as the starting experiment. Do not supply held-out supervised model scores as allegedly label-free features.

### 7. Real biological campaign bundle — keep 3/5 conditionally

This is closest to the thesis but is not yet one turnkey benchmark. Its score should depend on successfully reconstructing informative histories, not on combining attractive project names.

| Dataset | What the inspected sources support | Main issue / practical use |
|---|---|---|
| ALDE | Code for the real ParPgb campaign plus simulations on complete GB1/TrpB landscapes; the linked archive is 5.9GB. | Distinguish real campaign observations from simulation labels. The authors explicitly say unmeasured production labels are zero placeholders and production regret is meaningless. Never treat those zeros as failed experiments. |
| SAMPLE | The institutional/paper pages describe four agents optimizing glycoside hydrolase thermostability and point to the supplied Zenodo DOI for code/data. | Four agents searching the same underlying objective are not four independent biological problems. The archive could not be opened in this audit; completeness and reuse terms remain unverified. |
| Metalloenzyme active learning | Zenodo has a 365.5KB raw assay/library archive, separate embeddings and structures. | Start with measured tables and batch/library identifiers. The code README says its extensive original benchmark needs the authors' MongoDB, so do not promise full original reproduction from public scripts alone. |
| Cell-free biofoundry | Three small archives are described as data generated/used during active-learning loops, totaling about 822KB. | Inspect batch lineage, formulation variables, controls and measurement comparability. Three archives do not automatically imply three independent scientific problems or a dense outcome oracle. |
| SDLGuide | A 55MB software archive includes a representative autonomous glucose-oxidase assay optimization dataset. | Useful for feasibility, constraints and execution history. A tutorial campaign is a small source of training variation and should not carry a broad transfer claim alone. |

Sources: [ALDE code](https://github.com/jsunn-y/ALDE), [ALDE archive](https://zenodo.org/records/12196802), [SAMPLE institutional record](https://www.glbrc.org/data-and-tools/glbrc-data-sets/self-driving-laboratories-autonomously-navigate-protein-fitness), [metalloenzyme archive](https://zenodo.org/records/12578395), [metalloenzyme code](https://github.com/lasgroup/ml-protein-design-sav-gold), [cell-free archive](https://zenodo.org/records/14904992), [SDLGuide archive](https://zenodo.org/records/19190906).

Proposed test: leave one independent campaign system out, then test whether earlier measured histories improve forecasts/rankings of its later measured batches. Keep entire campaign systems together. Compare rich-history training with a flat-outcomes version using the same measurements, plus a frozen system. Add history-order and feedback controls. An extra ablation should distinguish ordering from simply receiving additional metadata or labels.

If the measured candidate union gives comparable outcomes under one assay protocol, it can support selection replay restricted to that measured union. Disclose that historical selection bias remains. It cannot establish the value of arbitrary alternative experiments never measured in the source campaign. A fitted surrogate is a separate simulator study, not experimental ground truth; do not train and judge a policy using the same surrogate as if it were a laboratory.

The inspected SDLGuide tutorial CSV contains 40 observations assigned to iterations 1–5, additional measured rows without iterations, and empty placeholders. This is a small integration fixture, not a large training corpus. [Actual CSV](https://raw.githubusercontent.com/GormleyLab/SDLGuide/main/Hands-on%20Tutorial/GOx%20Assay%20data_bank_renamed.csv).

Run a 48-hour completeness/schema audit. Proceed with the usable subset, document exclusions, and record what can actually be evaluated. The bundle is useful even if the first result is limited to chronology-aware transfer prediction. Public availability and a code license are not blanket evidence of commercial rights to all data and embedded material; resolve the specific ambiguous artifacts before commercial training.

### 8. Pfizer HiTEA — keep 3/5; run early

The full release contains over 39,000 condition experiments covering more than 350 target products over roughly ten years. The repository supplies full/cleaned data. This is genuine breadth, but target products are not automatically independent industrial projects. The paper also explains selection biases, sparsity and limitations of yield measurements. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10997498/), [code/data](https://github.com/emmaking-smith/HiTEA).

Proposed test: group by target product and reacting substrates/scaffolds, then check whether genuine project IDs and timestamps permit stronger project/temporal holdouts. Begin within reaction classes instead of immediately claiming chemistry-wide transfer. Restrict choices to measured condition rows within each held-out screen. Compare random, a global best-condition prior, a fingerprint/tree ensemble and uncertainty-aware optimization with learned transfer selection. Preserve zero-yield data and distinguish missing measurements from zeros. Use all raw outcomes only on the evaluator side; do not expose full-screen Z-scores fitted with hidden outcomes as inputs.

Measure experiments needed to find a useful yield/selectivity threshold and best observed outcome at budget. The defensible result concerns held-out recorded screens under their supported condition menus. It is not unrestricted reaction discovery or proof of what would have happened outside the measured support. The advantage is a cheap second domain with clear industrial relevance.

### 9. JUMP Cell Painting — 3/5 for a cross-lab data product; 2/5 for this scientist thesis

JUMP provides multiple data levels, including well-aggregated profiles and metadata across 12 data-generating centers. Start with those profiles and actual overlap between centers, not raw images or billions of cells. [Official data description](https://broadinstitute.github.io/jump_hub/explanations/data_description.html).

Two different tests are needed: (a) predict/retrieve an already-seen perturbation in a new lab; (b) predict an unseen perturbation or chemical scaffold in a new lab. Success on (a) is not success on (b). Split whole centers and plates; do not split individual cells or replicates as independent units. Fit preprocessing on training data, permitting target-lab negative controls only if the protocol explicitly allows them. Inspect supplied batch-corrected profiles for transductive use of held-out perturbation measurements.

Compare control/mean, same-compound nearest-neighbor, simple regression and accepted batch-correction baselines. Score phenotypic effect recovery/retrieval and calibration, and compare with replicate reproducibility. More sample agreement after batch correction is not automatically biological prediction or a better experimental decision. Run this if cross-lab standardization or transfer is a candidate product; otherwise prioritize selection tests.

### 10. Arc Virtual Cell — 3/5 for prediction with external assessment; 2/5 for scientist decisions

The 2026 task supplies unperturbed controls and gene targets for six cellular contexts, with perturbation outcomes withheld. Three contexts support validation and three final testing; no challenge-specific training set is released. Other public training data are allowed. Final submissions are due **5 November 2026**, eight days after this report; final test inputs were scheduled for 22 October. [2026 announcement](https://arcinstitute.org/news/virtual-cell-challenge-2026).

Use the 2025 public data and other allowed public perturbation datasets for development, a reproducible existing model as the baseline, and one deliberately scoped data-adaptation comparison. Preserve the same architecture, representation and evaluation pipeline between frozen and updated arms. Check current submission rules before assuming multiple matched official entries are permitted. Treat 2026 validation feedback as validation, not an independent test.

Report differential effects, perturbation discrimination and the complete official metric set, not just similarity dominated by unchanged genes. Arc's 2025 wrap-up explicitly discusses strong statistical baselines and metric trade-offs. [2025 lessons](https://arcinstitute.org/news/virtual-cell-challenge-2025-wrap-up).

A reasonable compact-model/summary-data entry is feasible this week; training a new foundation model is unnecessary. The result supports improved cross-context intervention prediction, not choosing experiments or interpreting surprises. External scoring cannot prove our data's marginal value unless the matched training-data ablation is actually carried out.

## Screen of every lower-scored entry

| Original rank | Revised usefulness for this thesis | Decision and reason |
|---|---|---|
| 11 RoboChem-Flex / Minerva | 2 standalone; useful additions to #7/#8 | Both are valuable genuine campaign sources, not independent platforms to start from scratch. Minerva releases 1,632 measured reactions and reports its original calculations used a 24GB RTX3090. RoboChem-Flex releases optimization data as well as simulation outputs; keep these evidence types separate. [Minerva](https://github.com/schwallergroup/minerva), [RoboChem-Flex](https://www.nature.com/articles/s44160-026-01053-0). |
| 12 TadA-Bench | 2 standalone; useful transfer holdout | Its card describes 31 evolution rounds. Use chronological future-round evaluation and avoid sequence leakage. Many related variants/rounds remain one enzyme family. Useful after broader training, not a replacement for multiple held-out families. [Card](https://huggingface.co/datasets/JinGao/TadA-Bench). |
| 13 Autonomous Science Bench | Raise to 3 as an evaluation adjunct | Useful ready-made budgeted interfaces and separate discovery/learning gates. The README explicitly distinguishes measured replay, digital twin, and live-lab interface contracts. Count only measured replay as experimental evidence; keep task families held out from training. Freeze the evolving task roster and inspect backend data. It is not itself a broad training corpus. [Repository](https://github.com/Yibo-Wen/as-bench). |
| 14 LabOS LSV / proteomics practice | 2 for supervision; lower for scientific transfer | Useful for monitoring a declared procedural error. Hold out operators/protocol families/sites and related camera views. Visible error recognition does not establish downstream assay harm or successful recovery. LSV lists a noncommercial license; the proteomics archive could not be directly opened here. [LSV](https://huggingface.co/datasets/cong-lab/lsv), [proteomics record](https://doi.org/10.5281/zenodo.17710382). |
| 15 BEAR materials failures | 2 | Could test the marginal value of execution/failure metadata versus endpoint-only data. Mechanically concrete and useful as another domain, but not a reason to start a materials business. The provided record returned 403 in this audit; the asserted license and actual files were not reverified. [Record](https://open.bu.edu/items/871d47cb-a12c-4ebb-8623-92df97353ea9). |
| 16 Binder assay disagreement | 2 conditional | One of the better tests of interpreting surprising evidence, but only if a defensible reference assessment can be constructed. Two vendors disagreeing does not reveal which is right; the combined final label is not independent of its constituents. Consider blinded expert adjudication and reserved orthogonal evidence. [Dataset](https://huggingface.co/datasets/Anthropic/claude-protein-binder-design). |
| 17 Binder prediction update | 2 | Cheap prediction study. Use held-out targets and pre-experiment features only; distinguish non-expression, missing/failed assays and true nonbinding. Fine-tuning must beat calibrated simple baselines on a business-relevant endpoint. Same source as #16, not independent evidence. |
| 18 GFP forecasting | 1–2 for this thesis | Defer physical generation without a monitoring/forecasting buyer. A successful forecast is not broad experimental reasoning. |
| 19 ToxCast / PRISM | ToxCast 2; promote PRISM to 3 for screening | PRISM's primary screen is a promising alternative measured lookup environment, with thousands of drugs across hundreds of cell lines. Train on some contexts and hold out lineages; separately test chemical-scaffold transfer. Use primary-screen measured cells with QC and count missing entries as unavailable, not inactive. Include global drug activity and nearest-context baselines. Selectivity matters: nonspecific toxicity must not become the easiest definition of success. Secondary dose-response follow-up is a selected subset. Cell lines are contexts, not independent studies. ToxCast needs careful separation of assay endpoints, cytotoxicity and readout artifacts. [PRISM](https://depmap.org/repurposing/), [processing code](https://github.com/broadinstitute/repurposing), [ToxCast](https://www.epa.gov/comptox-tools/toxicity-forecasting-toxcast). |
| 20 LabSafe-1700 / FineBio | 2 for robotics; 1 for scientific reasoning | Perception/manipulation training can be valuable but answers a separate product question. Separate demonstrations/views/actors in splits. Check actual physical-policy transfer rather than treating action recognition as robot execution competence. [LabSafe](https://huggingface.co/datasets/Merlyn-L/LabSafe-1700), [FineBio](https://github.com/aistairc/FineBio). |
| 21 IronMind | 2 evaluation; useful training adjunct | Convenient optimizer/human/LLM histories, but their underlying landscapes are the important split unit. Different objective columns and seeds on the same landscape are not independent tasks. Useful supervised imitation/ablation source if tested on wholly different measured chemistry; do not treat reasoning text as a verified cause of success. [Dataset](https://huggingface.co/datasets/gomesgroup/iron-mind-data). |
| 22 Record ordinary CRO work | 2 generic; potentially 3 with a controlled partner design | More cameras/logs alone do not validate data value. Compare matched training using outcomes only versus additional selected execution metadata on independent projects/sites. Define that ablation before collecting everything. |
| 23 Open-ended discovery program | 2 for data thesis; potentially valuable separate company | A useful discovery demonstrates discovery value. To demonstrate training-data value, train another system on the resulting data and test transfer to separate problems. Do not combine those claims. |
| 24 BioDiscoveryAgent replay | 1 standalone; retain as engineering fixture | The existing split has only one held-out study; broadening the benchmark is higher priority than an expensive sweep of this small split. |
| 25 GB1/FLIP | 1 standalone; retain as optimizer smoke test | Useful for software and epistasis-sensitive acquisition. Keep out of both training and purported independent validation if the same GB1 data are also used through ALDE/ProteinGym. [FLIP](https://github.com/J-SNACKKB/FLIP). |
| 26 Robin / archived modeling campaigns | 1 standalone; selective auxiliary training | Robin artifacts can reveal workflows; the modeling archive concerns three discovery runs plus reconciliation/refinement of one underlying biological modeling case. Useful for model revision but not multiple independent biological investigations or verified causal reasoning. [Robin](https://github.com/Future-House/robin), [archive](https://zenodo.org/records/23453778). |
| 27 OpenDiscoveryTrace / SciAgentTrace | 1 | Useful generic agent/tool-use adaptation controls. Audit source tasks, synthetic components and per-source rights. Improved trace imitation is not evidence of experimentally grounded scientific capability. [OpenDiscoveryTrace](https://huggingface.co/datasets/aayambansall/OpenDiscoveryTrace), [SciAgentTrace](https://huggingface.co/datasets/AgentsSci/scientific-agent-protocol-traces). |
| 28 OpenCell | 1 for this thesis | Useful representation/prior resource, not a direct sequential-investigation benchmark. The supplied download page was not text-readable in this audit. [OpenCell](https://opencell.sf.czbiohub.org/download). |
| 29 Summit | 1 as scientific evidence; useful infrastructure | Good optimizer regression tests. Label measured-table replay and fitted/mechanistic emulator results separately. Model optimization on a simulator is not a new laboratory result. [Docs](https://gosummit.readthedocs.io/en/latest/experiments_benchmarks/implemented_benchmarks.html). |
| 30 RxnOptBench | Keep unscored pending access; likely ancillary | The inspected paper describes source-table condition questions and future final-release arrangements. It is not evidence that arbitrary chemical condition outcomes are available for sequential replay. If available, split by parent publication/table; thousands of questions do not equal thousands of independent screens. [Paper](https://arxiv.org/html/2610.02242v1). |
| 31 Full Ginkgo/OpenAI CFPS histories | Keep unscored pending actual data | The public repo describes an automation interface and experiment schemas. Complete histories/outcome access was not established. Potentially valuable once specific artifacts and usable rights are confirmed. [Repository](https://github.com/ginkgobioworks/ginkgo-automation-cfps). |

## Capacity and timing

Assume RTX **A6000** (Ampere, 48GB), not RTX6000 Ada or RTX PRO6000. It is sufficient to begin these quantitative studies. Pair it with 16–32 CPU cores, 128GB RAM and 1–2TB local SSD; CPU preprocessing and I/O matter for JUMP and Arc. Stream/aggregate profiles rather than loading raw images or entire single-cell corpora unnecessarily. [NVIDIA specifications](https://www.nvidia.com/en-us/products/workstations/rtx-a6000/).

The following are planning ranges, not measured runtimes. They assume processed data, cached/frozen representations, compact supervised/selection models, conventional baselines and a modest repeated comparison. No new foundation-model pretraining, full raw-image reprocessing, structure prediction for every variant, or exhaustive RL search is included. First signal means a real baseline result, not scientific confirmation. Single-A6000 GPU work is an approximate total across jobs; wall time also includes CPU work, downloads and audit. The faster plan uses independent jobs across 2–4 H100s where useful, not an assumption of perfect distributed scaling.

| Originally score-3 experiment | First runnable baseline/signal after usable access | Approximate single-A6000 GPU work for scoped study | Elapsed on A6000 + AI-assisted engineering | Elapsed with CPU capacity + 2–4 H100s |
|---|---|---:|---|---|
| ProteinGym selection | 0.5–1.5 days | 100–400 hours | 1–3 weeks | 3–7 days |
| Five-source real campaign bundle | 1–3 days for schema/coverage audit | 20–100 hours | 4–10 days | 3–7 days; missing data/rights delays excluded |
| HiTEA selection | 0.5–1 day | 10–80 hours; often mainly CPU | 2–5 days | 2–4 days |
| JUMP well-profile transfer | 1–2 days | 30–150 hours | 4–10 days | 3–7 days |
| Arc compact-model adaptation/entry | 1–2 days | 100–600 hours | 1–4 weeks | 4–8 days for a tightly scoped existing-model entry |

For the campaign bundle, initial source-specific targets are below. These are AI-assisted parsing plus classical/compact-model baselines, not three-seed LLM training studies:

| Source within #7 | First narrow baseline after usable file access | Compute requirement |
|---|---|---|
| ALDE complete landscape / real ParPgb table | 2–8 hours | CPU baseline; up to several A6000-hours for optimizer comparisons |
| SAMPLE historical-round data | 4–12 hours | CPU GP/uncertainty baseline; GPU optional |
| Metalloenzyme measured tables | 3–8 hours | CPU descriptors/GP/ensemble; GPU optional |
| Cell-free formulation tables | 3–8 hours | CPU GP/tree baseline; GPU optional |
| SDLGuide | 1–3 hours | CPU; generally no GPU needed |

An individual source can often yield a baseline in hours once its table is understood. Cross-source normalization and valid evaluation dominate the 3–7 day combined schedule. There is no finite promised end date for a missing archive, unavailable database or unresolved access. These are not GPU tasks.

If the intended claim specifically requires **LLM weight training**, add an explicit second layer: base versus outcomes-adapted versus history-adapted versions of one 7–14B model, repeated with three training seeds. A compact retrieval/selection tool must serve candidates and observations consistently, rather than printing million-row libraries in prompts. Budget another **100–1,000 H100 GPU-hours per domain** for scoped fine-tuning and thousands of inference decisions; profile and revise this range. Training tokens, context length, output length and inference call count determine that cost. A specialist-only win cannot be relabeled as improved general reasoning by the base LLM.

Do not assume H100 is a universal fixed multiple faster than A6000. Benchmark actual jobs for one hour. Use the A6000 for preprocessing/debugging/compact models, H100 for repeated training and parallel model runs, and H200/B200 only where memory/context or measured throughput justifies them. H200 has 141GB VRAM; this can avoid model/context sharding but does not guarantee statistical value. [H200 specifications](https://www.nvidia.com/en-us/data-center/h200/).

## €100,000 compute budget

The budget is ample for these scoped experiments. More compute should buy independent holdouts, data-volume ablations, additional training seeds, strong baselines and a second domain before it buys a bigger model.

At the inspected Runpod list prices, RTX A6000 is $0.59/hour, H100 SXM $3.99/hour, H200 $5.29/hour and B200 $7.99/hour. These are examples of advertised configurations, not a quote or guarantee of availability; storage, tax, region and currency conversion affect the bill. [Pricing, inspected 28 October 2026](https://www.runpod.io/pricing).

Use **€5/H100 GPU-hour as a conservative internal budgeting assumption**, not a converted supplier rate. Four GPUs running for 14 days consume 1,344 GPU-hours, or €6,720 under that assumption. An 8-GPU instance costs for all eight GPUs even if only one is effectively used. Hosted teacher/agent API calls, if chosen, are separate from self-hosted GPU hours.

Proposed allocation, not a purchase instruction:

- First sweep: ceiling €10,000 for the ProteinGym/HiTEA primary studies, campaign audit, and cheap JUMP/Arc feasibility baselines; use only a fraction if compact models answer the question.
- Robust follow-up: up to €20,000 for matched LLM adaptation where relevant, three training seeds, held-out-family replication, scaling with training-data quantity and a clean second-domain test.
- Hold €70,000 as reserve until a specific result shows what additional compute would resolve. A foundation-model effort is a different scope and should not consume this reserve by default.

## Proposed start order

Day 1: freeze sources; run representative ProteinGym and HiTEA baselines; verify family/product holdouts; audit the five real-campaign schemas. If Arc is strategically wanted, reproduce one existing-model baseline immediately because of the 5 November deadline.

Days 2–3: complete a small matched train/update comparison and feedback ablations; run AS-Bench measured-replay sanity checks; inspect PRISM as a potential broader biological selection environment. Cache expensive representations once.

Days 4–7: finish the accelerated primary comparisons, including held-out groups and confidence intervals; decide whether a richer history or larger training set changes the result. Keep final holdouts untouched until model selection is fixed. Complete the scoped Arc submission only if its data-adaptation result is interpretable and the official rules permit it.

Weeks 2–3: extend the strongest result across independent data groups and training seeds, and run the explicit LLM experiment if that is the commercial claim. Use real campaign histories to identify what richer metadata actually buys. Nothing here yet justifies claiming all aspects of a better scientist, but a narrow capability improvement can be useful and commercially meaningful.

CEO note: We have enough compute to execute decisively. The first win to seek is a repeatable reduction in experiments needed on unfamiliar problems. The main danger is spending weeks improving a score whose split or ground truth cannot support the business claim.

An [earlier detailed campaign-source audit](2026-10-28-campaign-source-audit.md) is preserved alongside this report. The portfolio scope and runtime assumptions above supersede earlier narrower estimates where they differ.

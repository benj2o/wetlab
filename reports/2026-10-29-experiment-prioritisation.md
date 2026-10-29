# Experiment prioritisation and run order — 29 October 2026

Independent review of the [handoff inventory](../HANDOFF.md) and the [28 October audit](2026-10-28-dataset-audit-and-compute.md). This re-scores every listed experiment, adds nine that were missing, and commits to a run order.

Provenance is marked throughout: **[V]** verified by fetching the source in this session; **[V-sub]** verified by the dataset-search agent this session; **[C]** claimed by a paper, dataset card or secondary source and not verified. Everything unmarked is inherited from the prior audits or the research notes and carries their original confidence.

## Decision

**The single most important finding is that a better corpus than ProteinGym exists for the core claim, it is MIT-licensed, and it was not in the inventory.**

**BioGRID ORCS** [V]: version 2.0.18 indexes **2,217 CRISPR screens from 418 publications, 825 cell lines, 145 cell types and 5 species**, under the **MIT License, explicitly free to commercial users**. For comparison, the Genentech AssayFormer result — the strongest published evidence for our thesis — was trained on 1,389 screens from a single company's internal corpus, split temporally. ORCS is larger *and* partitions by publication and laboratory, which is the generalisation Genentech explicitly could not test.

One honest caveat on that comparison: AssayBench-Loop's 1,389 are all **genome-wide** screens, whereas ORCS's 2,217 include focused and targeted libraries. The usable count after filtering to a consistent screen type will be lower than 2,217, and possibly lower than 1,389. The durable advantage is not raw count — it is the **418 independent publications and 825 cell lines**, which no single-institution corpus can offer at any size.

The run order follows:

1. **Calibration bundle** (days 1–3, ~€0): assay noise floor, memorisation probe, lab-identity probe. Each gates expensive work.
2. **Harness on real data** (days 3–5): the BDA replay we already built, with its two unused screens added.
3. **ORCS selection benchmark and scaling curve** (days 5–14): the main event, and the only experiment that puts a price on a campaign.
4. **Process-versus-endpoint ablation** (days 10–18): the control that decides whether to build a laboratory.

ProteinGym moves to week 3+ as a second-modality replication. Arc Virtual Cell is killed. All video, robotics and physical-generation items are deferred.

The reordering rests on one judgment: the prior audit chose experiments by *breadth of data*, which makes ProteinGym the flagship. Breadth was never the binding constraint. The binding constraint is that nothing in the inventory discriminates between "training on experimental records works" — already published by someone else — and "training on *our kind* of record beats a cheaper substitute", which is the actual business.

## What changed since 28 October

Five facts established in this session that the prior audits did not have.

**Network access is restored.** [V] The 28 October audit was written with GitHub DNS unavailable and recorded that "public datasets have not been downloaded, cleaned or benchmarked locally." GitHub, Hugging Face, Zenodo, DepMap and BioGRID all respond 200; `git ls-remote` succeeds. The BioDiscoveryAgent master commit is `19673c7371c542cfa155ffaa9047c53525f9fe2e` — pin this, the experiment README asks for it.

**Local disk is exhausted, and this is now the blocker.** [V] 689 MB free on a 494 GB container; `/System/Volumes/Data` is at 100%. `~/Downloads` is 33 GB, `~/Library/Caches` 21 GB. NumPy, SciPy, pandas, scikit-learn and Torch are all absent from the system Python 3.9.6, and the machine is 8 cores / 16 GB. The "CPU preprocessing, hours locally" assumption in the compute plans is currently impossible. ORCS gene-level tables for 2,217 screens will not fit in 689 MB (exact archive size unverified — the download index is JS-driven and rate-limited me). **Free ~50 GB or provision the rented box before day 1.** This is the only hard blocker in the plan.

**The BDA benchmark has eight screens; our split uses six.** [V] The full `datasets/` directory is **6.9 MB** and fits in the free space. Two screens are ignored by `configs/split.json`:

| Unused screen | Rows | Why it matters |
|---|---:|---|
| `Steinhart_crispra_GD2_D22` | 18,797 | **CRISPRa** (activation). Every screen in the current split is knockout or interference. A different perturbation modality is a genuinely independent problem. |
| `Horlbeck` | 100,576 | **Gene *pairs*** — combinatorial interactions, not single genes. A different task structure. |

The handoff scores #24 a **1** on the explicit grounds that "current IFNG/IL2 holdout is one study, not two independent problems." The criticism is correct — IFNG and IL2 are both Schmidt — but the remedy is already in the repository at zero cost. Steinhart takes independent held-out studies from one to two across a modality shift; Horlbeck supports a third, harder probe.

**The binder dataset is ungated and CC-BY-4.0.** [V] `Anthropic/claude-protein-binder-design`, 39,524 downloads, `license:cc-by-4.0`, not gated. Per-replicate raw BLI traces, fitted curves, refits and buffer-blank controls from two vendors. The internal tracker's "Ready to start, ~£0" is accurate, and it has been ready for ten days. Commercially cleaner than most Zenodo archives in item #7.

**Nine datasets worth adding were found, and several rejections are informative.** Full detail in the table below. The most consequential rejections [V-sub]: DrugComb/NCI-ALMANAC and Tox21 have large row counts but only ~8–10 and ~30–60 independent problems respectively; LINCS L1000 is one production pipeline; a Hugging Face search for round-structured directed-evolution corpora returned **zero** results beyond TadA-Bench. There is no hidden trove of multi-round protein-engineering data. That absence is itself a finding — it is the gap a data business would fill.

## The thesis, decomposed

The business requires five claims. Scoring an experiment means asking which one it discriminates.

| | Claim | Status in the published record | Tested by |
|---|---|---|---|
| **C1** | Experimental records train a better experiment-*chooser* | **Established by others.** AssayFormer: EF 4.83 on held-out CRISPR screens; RL adds +1.00 over the supervised stage | NEW-F, #6, #8, #19a, #24 |
| **C2** | The gain *transfers* to unfamiliar problems | **Partly.** Leave-one-phenotype-out 4.59 vs 4.83 — but only across phenotype categories inside one task family | NEW-F, #24-expanded, #8 |
| **C3** | The gain comes from *process structure*, not just more labels | **Essentially untested.** One internal null (ESCALATE ridge, MAE 0.8610→0.8609) | NEW-E, #7, #15 |
| **C4** | Data value *scales* with campaign count | **Established by others, never replicated.** AssayFormer: monotonic in training screens, no plateau; ~40× parameter increase buys little | NEW-D |
| **C5** | The learnable signal is biology, not laboratory identity | **Adverse evidence.** Protein-failure benchmark: PR-AUC/base 1.85 within-centre vs 1.01 across centres (random 1.03), despite cross-centre training sets 4.0–17.7× larger | NEW-C, #9 |

**C3 is the company.** If a $90/hour expert writing "it failed because the antigen aggregated" buys the same lift as the execution trace, there is no reason to instrument a laboratory. The internal documents already named this — "the control that decides the company", C2b in Experiment-01 — and never ran it. Nothing in the current inventory is scoped to answer it directly, though #7, #15 and two newly found SDL archives contain the raw material.

**C1 is largely spent.** Re-demonstrating "training on screens improves selection" is replication. Worth having; not worth going first. What is *not* spent is C1 **with cross-laboratory holdouts**, which ORCS uniquely enables and which no published result covers.

### The strategic caveat nobody has priced

AssayFormer beat the best prompted LLM 4.83 to 4.81 — a rounding error. The trained *specialist* scales and transfers. But **AssayLLM** — the same data used to post-train a 27B LLM on acquisition trajectories — reached 3.69, below the frontier LLMs it was meant to beat and below its own teacher.

The one published attempt to do the exact thing this business proposes to sell data *for* underperformed prompting. On current evidence the value accrues to specialist policies. The sequencing consequence is direct: **run the specialist arm before paying for LLM fine-tuning.** It is cheaper, it is where the evidence says the signal is, and a specialist win is still a sellable product — to a different buyer than a frontier lab's post-training team.

## Scores

Ordinal priority for validating the main hypothesis, on the handoff's own rubric. "Discriminates" drove the run order: would a negative result change what we do next?

### Added — not in the inventory

| ID | Experiment / dataset | Score | Claim | Why | Cost |
|---|---|:---:|:---:|---|---|
| **NEW-F** | **BioGRID ORCS selection benchmark.** 2,217 screens, 418 publications, 825 cell lines, MIT [V]. Replay via the existing BDA harness, holding out whole publications and laboratories. | **4** | C1, C2 | Larger than the Genentech corpus and partitions by lab and publication, which theirs cannot. Licence is clean for commercial use. The strongest single addition. | 4–7 days |
| **NEW-D** | **Campaign scaling curve.** Train on N = 1, 2, 4, 8 … 400 publications; plot held-out performance against N. | **5** | C4 | The demand curve. A flat curve means one corpus suffices and there is no recurring revenue; a rising curve prices a campaign. ORCS makes this runnable at a scale nobody has published. | +2–3 days on NEW-F |
| **NEW-E** | **Synthetic-explanation control.** Arms: outcomes only / + ordering / + real execution metadata / + LLM-written post-hoc rationale, at matched tokens. | **5** | C3 | The kill switch. Cheap text matching real traces ends the laboratory thesis. | 4–6 days |
| **NEW-C** | **Lab-identity confound probe.** Can a classifier recover the source laboratory from the biology? Does measured transfer survive a site holdout? | **4** | C5 | Existential for a multi-site data business, with adverse prior evidence. Two off-the-shelf substrates now exist (below). | 1–2 days |
| **NEW-G** | **WhatWorkedBench** [V-sub]: 36 task conditions, 30 sources, agents *buy* 8 measurements + 2 free anchors, graded against exhaustive reference results. | **3** | method | Not physical experiments, so it cannot validate the data thesis — but it runs the complete (unchanged / outcomes / histories / conventional) design with a shuffled-feedback control at zero cost and zero licensing. A methodological rehearsal that de-risks every later study. Repo URL unconfirmed [C]. | 2–3 days |
| **NEW-A** | **Assay noise floor.** Convert two-vendor agreement and replicate structure into a reliability coefficient and a minimum detectable effect. | **3** | prereq | Bounds every later claim. Internal counts already give 1,235 designs at both vendors with 89.0% agreement — if reproducibility caps near that, a 5% uplift is unmeasurable on this assay. | 1 day, €0 |
| **NEW-B** | **Memorisation probe.** Can the base model rank held-out DMS variants with no feedback, beyond what its zero-shot structural prior predicts? | **3** | prereq | Gates #6 and #25. A positive result makes LLM arms on heavily-published DMS uninterpretable. | 1 day |
| **NEW-H** | **PubChem primary→confirmatory links** [V-sub, predicates seen on rdf.ncbi.nlm.nih.gov]: machine-readable `is_confirmatory_assay_of` triples linking primary screen → dose-response follow-up. | **3** | C1, C2 | Observed *human* experiment-selection decisions at scale — which hits a real screening team actually carried forward. Nothing in the inventory has a human-policy target. Live statistics page is CAPTCHA-blocked; go via FTP/RDF. | 3–5 days |
| **NEW-I** | **ChemWorld fork pairs** [V-sub]: 6 parent–child worlds differing by exactly one hidden law, with transactional logs of operations *and failures*, replayable exactly. | **3 cond.** | — | The only instrument found for "revises its explanation when a surprising result arrives" — the part of the thesis that currently has *no* measurable instrument at all. Conditional: no repository or licence on the abstract page. Worth one email. | unknown |

NEW-A and NEW-B score 3 rather than 5 because neither validates the thesis — they make other results trustworthy. They run first because they are nearly free and gate expensive work.

**Substrates for NEW-C** [V-sub, counts claimed by sources]: the **Genetic Engineering Attribution Challenge** (81,833 plasmid sequences labelled with **1,314 laboratories of origin**, established leaderboard) is a literal, off-the-shelf "can a model identify the lab rather than the biology" probe. **MARCO** (~493,214 crystallisation images from **5 institutions**, ~70% inter-annotator agreement, documented cross-site degradation to 82%/49%) adds measured label noise and measured cross-site collapse. Together these are a better C5 instrument than the JUMP slice I would otherwise have used, and need no wet lab.

### Re-scored

| ID | Experiment | Handoff | Mine | Reasoning |
|---:|---|:---:|:---:|---|
| 6 | ProteinGym | 4 | **3** | **Disagree.** A fair 4 as a selection test with real family holdouts, and I would hold it at 4 if the question were only "can we measure selection transfer." Lowered on decision value: it is an outcome table, so it structurally cannot address C3 — the audit concedes this ("outcome data rather than original decision history") and still makes it the flagship. ORCS now dominates it for C1/C2 on holdout count, cross-lab structure and licence. Add contamination risk on heavily-published DMS. Run it as replication in week 3. |
| 24 | BioDiscoveryAgent replay | 1 | **3** | **Disagree.** Scored 1 for having one held-out study — true of the configured split, not the dataset. Steinhart and Horlbeck are sitting unused [V]. The harness is built and its tests pass. Its real value is as the validated on-ramp to NEW-F: same interface, same controls, 6.9 MB of data, running today. |
| 15 | BEAR | 2 | **3** | **Disagree, raise.** One of very few sources with real execution and failure metadata against endpoints, which makes it substrate for NEW-E. Materials domain is a weakness for the headline claim and irrelevant for the ablation. Returned 403 in the prior audit — reverify early. Two newly found SDL archives [V-sub] are alternatives: an enzymatic-electrochemistry set (>10,000 voltammograms with enzyme, substrate, scan-rate and **replicate index**, CC BY 4.0) and a metal-electrodeposition SDL (554.8 MB, **ships the execution scripts alongside the data**, CC BY 4.0). |
| 13 | Autonomous Science Bench | 3 | **2** | **Disagree, lower.** An evolving third-party roster is a poor dependency, and we need our own held-out evaluation before an external one. NEW-G is the better methodological rehearsal. Keep as a later independent check. |
| 9 | JUMP Cell Painting | 2 | **2** | **Agree, and now superseded for its best use.** I would have raised the cross-lab slice to 4, but GEAC and MARCO do that job more directly and far more cheaply. Leave JUMP at 2. |
| 10 | Arc Virtual Cell | 2 | **Kill** | **Disagree with keeping it conditional.** Submissions close 5 November: seven days, no trained baseline, no GPU, no pipeline. Prediction-only, which the rubric caps at 2. A conditional entry against a hard external deadline will consume attention all week. Close it explicitly. |
| 16/17 | Binder interpretation / prediction | 2 | **2** / **3** | Prediction and adjudication stay at 2. The noise-floor slice (NEW-A) is a 3 and runs immediately. |
| 7 | Campaign bundle | 3 cond. | **3** | **Agree on the number, disagree on the use.** As a transfer test it is hopeless: ALDE (one real campaign), SAMPLE (four agents, one objective — one problem), metalloenzyme (one design space), cell-free (three related systems, one study), SDLGuide (one tutorial) is about five independent problems, and no interval over five means anything. Re-scope as process-metadata substrate for NEW-E, where genuine round structure is exactly what is needed. |
| 14, 20 | LabOS LSV, LabSafe-1700 / FineBio | 2 | **1** | A robotics and supervision business with its own buyers and validation. Noncommercial licence on LSV. Not this thesis. |
| 23 | Open-ended discovery | 2 | **1** | A different company. Pursuing it dilutes the data claim. |
| 18 | GFP forecasting | 2 | **Defer** | Agree with the audit. No buyer named; a clean forecast would still be strategically weak. |
| 8 | HiTEA | 3 | **3** | **Agree.** Best second domain: 39,000+ condition experiments, 350+ products, ~10 years, real project and temporal structure. |
| 19a / 19b | PRISM / ToxCast | 3 / 2 | **3** / **2** | **Agree.** PRISM remains the strongest biological screening environment after the CRISPR corpora. Selectivity must be the endpoint or nonspecific cytotoxicity becomes the easy win. |
| 11, 12, 21, 22 | RoboChem/Minerva, TadA-Bench, IronMind, CRO recording | 2 | **2** | **Agree.** On #22: the ablation cannot be designed until NEW-E says which metadata carries signal. Instrumenting first would be instrumenting blind. |
| 25–29 | GB1/FLIP, Robin, traces, OpenCell, Summit | 1 | **1** | **Agree.** Smoke tests, representations, infrastructure. Deduplicate GB1 across FLIP / ALDE / ProteinGym before counting it anywhere. |
| 30, 31 | RxnOptBench, Ginkgo CFPS | unscored | **unscored** | **Agree.** No verified access. |

Also worth logging for later, not scheduled now [V-sub]: **ChEMBL** (~101k source documents, ~1.97M assays with publication years [C], CC BY-SA 3.0 [V-sub]) is the only route to independent holdouts in the thousands with a true temporal split; **CACHE** (9 targets × ~20 teams of blinded prospective selections with wet-lab readout, released without use restrictions [V-sub]) is the only corpus offering a human-expert policy baseline; the **ORD C–N coupling set** (50,688 reactions from one systematic campaign [C]) would make a chronological-versus-shuffled ablation confound-free in a way heterogeneous corpora never are.

No experiment reaches 5 on the handoff's definition, which reserves it for fresh or blinded investigations. NEW-D and NEW-E score 5 as *priorities* while remaining retrospective. That is a deliberate departure: the rubric reserves 5 for an evidential standard nothing retrospective can meet, which leaves it unable to express "this is the thing to do next."

## How the findings combine

**NEW-D × NEW-E is a 2×2 that names the business.** NEW-E says *what kind* of data to sell; NEW-D says *what a unit of it is worth*. Either alone is half an argument.

| | **Scaling curve rises** | **Scaling curve flat** |
|---|---|---|
| **Process beats endpoints** | The thesis as written. Instrumented lab network, recurring revenue per campaign. | Process data matters but one corpus saturates. A one-off dataset sale, not a data engine. |
| **Process ≈ endpoints** | Volume business in cheap outcome tables. Buy or scrape; do not instrument. No lab needed. | No data business. Pivot to the specialist-policy product, or to services. |

Three of four quadrants do not support building a laboratory. That asymmetry is the argument for running both before committing capital, and both are retrospective and affordable.

**NEW-A, NEW-B and NEW-C are one instrument-calibration bundle.** Individually unexciting; together they decide whether any later uplift number survives scrutiny. NEW-A gives the measurement floor, NEW-B rules out recall masquerading as reasoning, NEW-C rules out batch identity masquerading as biology. A buyer's technical reviewer will ask all three.

**#24-expanded → NEW-F → NEW-D is one pipeline.** Same harness, same controls, increasing stakes: 8 screens to validate the software on real biology, then 2,217 screens for the headline result, then the scaling curve over 418 publications. Each step reuses the previous step's code. This is why the low-scoring BDA replay runs before the high-scoring ProteinGym study.

**NEW-G de-risks the method before it is used on data that matters.** If history-training does not beat outcome-training in a controlled environment with exhaustive ground truth and a purchased-measurement budget, the problem is our training setup, not biology — and we want to learn that in two cheap days, not after the ORCS run.

## Run order

Gates are listed because the point of a cheap experiment is to stop an expensive one.

**Precondition — resolve disk.** Free ~50 GB, or provision the rented box and work there from hour one. Nothing below runs otherwise.

**Days 1–3 — calibration, ~€0, three in parallel**
- **NEW-A** noise floor. Binder summary tables only, not the 100k curve files. Deliverable: reliability coefficient, effective N, minimum detectable uplift. *Gate: if the floor exceeds our 10% continuation threshold, that threshold is unmeasurable on this assay and must be redefined before anything else runs.*
- **NEW-B** memorisation probe. *Gate: a positive result removes the LLM arm from ProteinGym and GB1, or forces a post-cutoff holdout.*
- **NEW-C** lab-identity probe on GEAC, with MARCO as the cross-site check. *Gate: if laboratory identity is highly recoverable and transfer collapses across sites, the multi-site plan changes and #9 drops out.*

**Days 3–5 — harness on real biology**
- **#24-expanded.** Prepare all eight screens at the pinned SHA. Revised split: train on Carnevale + Sanchez (both directions); validate on Scharenberg; hold out Schmidt (IFNG, IL2) *and* Steinhart. Keep Horlbeck untouched as a structural-transfer probe. Run the true / shuffled / hidden feedback controls already implemented. Specialist policy only — Linear-UCB and a trained acquisition model. Freeze the revised split in `configs/split.json` before looking at a single test outcome.
- **NEW-G** in parallel if a second pair of hands exists.

**Days 5–14 — the main event**
- **NEW-F** ORCS benchmark. Hold out whole publications and laboratories. Compare unchanged / outcomes-trained / history-trained / tuned conventional, at matched measurement budgets.
- **NEW-D** scaling curve over publication count, reported with source holdout — a rising curve driven by within-source protocol regularity is not transferable value.

**Days 10–18 — the control that decides the company**
- **NEW-E** process-versus-endpoint with the synthetic-explanation arm, on BEAR (or the two newly found SDL archives) plus the #7 bundle. Match tokens across arms and report matched-compute sensitivity, or the result is confounded by training budget.

**Weeks 3–4 — replication, conditional on the above**
- **#6 ProteinGym** cross-family transfer, if NEW-B clears it.
- **#8 HiTEA** cross-domain chemistry check, if NEW-D or NEW-E produced a positive worth generalising.

**Killed or deferred:** #10 Arc (deadline, wrong capability). #14, #20 video and robotics (different business). #18 physical GFP (no buyer). #23 open-ended discovery (different company). #13 as-bench (revisit as an external check). #22 CRO recording (blocked on NEW-E). #9 JUMP (superseded for its best use).

## Where this could be wrong

Stated plainly, so the plan can be attacked rather than relitigated.

- **ORCS screens are heterogeneous in a way that may defeat a single interface.** 2,217 screens across 5 species, 825 cell lines and 418 publications will have inconsistent score conventions, hit definitions and library coverage. Harmonisation could consume more time than the experiment. Mitigate by starting with the human subset and one screen type, and by counting usable screens after harmonisation rather than trusting the index count.
- **NEW-E may be underpowered.** Five campaigns with real process metadata is thin. A null will be ambiguous between "process data has no value" and "we had too little of it." Predeclare the detectable effect size given the sample and report a null as bounded, not conclusive. Ambiguity there argues for commissioning data — but sized to a power calculation we will have by then.
- **The scaling curve may reflect corpus homogeneity.** Campaigns from one source share protocols. Report with source holdout, not just campaign count.
- **Horlbeck may be too different to be informative.** Gene-pair selection could fail for interface reasons rather than capability reasons. Treat a failure as uninformative unless the mechanism is diagnosed.
- **Deprioritising ProteinGym is a real bet.** If the specialist arm is weak on BDA and ORCS, ProteinGym's curated breadth becomes the better substrate and this order should flip. The gate is the day-5 result, not another round of scoring.
- **None of this tests C6, whether anyone pays.** Zero buyers have stated a price. The strongest experimental result here leaves the commercial question untouched, and that one is answered by conversations, not compute.

## Addendum — licence and start-today status

All verified by direct API fetch in this session [V]. The 28 October audit recorded that "the Zenodo pages rendered blank license fields in this inspection for several records" and that the SAMPLE archive "could not be accessed." Both were rendering and access artefacts, not missing licences: **the Zenodo REST API resolves every one of them, and all three are CC BY 4.0.** SAMPLE downloads fine.

**Startable today — fits in the 689 MB currently free, licence clean:**

| Dataset | Licence [V] | Useful download | Score |
|---|---|---:|:---:|
| BioDiscoveryAgent (8 screens) | MIT | 6.9 MB | 3 |
| Anthropic binder (summary tables) | CC BY 4.0 | small subset of 100k files | 3 |
| Metalloenzyme — `assay_and_ML_data.zip` | CC BY 4.0 | 365 KB | 2 (NEW-E substrate) |
| Cell-free biofoundry (all 3 archives) | CC BY 4.0 | 822 KB | 2 (NEW-E substrate) |
| SAMPLE | CC BY 4.0 | 131 MB | 2 (NEW-E substrate) |
| SDLGuide | MIT | 55 MB | 1–2 (integration check) |

Total under ~200 MB. **The entire #7 campaign bundle plus the BDA screens fit in available disk today.** Only ORCS, ProteinGym and HiTEA require the disk to be cleared first.

Avoid for the metalloenzyme record: `structures.zip` is 4.98 GB and `data.zip` 1.75 GB. Neither is needed for the measured-table work.

**Licence clean, blocked only on disk:** BioGRID ORCS (MIT [V]), ProteinGym (MIT [V]), HiTEA (MIT [V]), ALDE (MIT, repo-level, prior audit).

**Not startable:** PRISM/DepMap (portal returns a bot-verification screen; licence unverified), Genetic Engineering Attribution Challenge (download availability unconfirmed), ChemWorld and WhatWorkedBench (no repository URL confirmed on either abstract page).

**Licence-disqualified for commercially-framed results:** LabOS LSV (noncommercial) and RxRx1 (CC BY-NC-SA 4.0). A noncommercial licence undermines any result presented as commercial validation — exclude these from partnership material regardless of their technical merit.

## Budget

Everything through day 18 fits inside the €10,000 first-sweep ceiling, and most of it inside €1,000 — the calibration bundle and the BDA replay are CPU work on megabytes. ORCS is the first item needing real storage and sustained compute. Hold LLM fine-tuning arms until the specialist arms produce a signal worth amplifying, per the AssayLLM caveat. Keep the €70,000 reserve untouched until NEW-D or NEW-E produces a number that says what more compute would buy.

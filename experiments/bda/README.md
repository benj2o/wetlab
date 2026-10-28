# Experiment 1: does experimental experience improve experiment selection?

**Decision: run ingestion, replay, baselines and analysis locally. Rent a CUDA GPU only after the pilot establishes a failure worth training against.** No laboratory spending. Colab is acceptable for an exploratory training notebook, but reproducible scripts and persistent run files are preferable for the actual comparison. No cloud resources or paid model requests have been started.

This is an implementation of a new training comparison using BioDiscoveryAgent's public screens, not a reproduction of the original agent or its full tools. Existing research notes were consulted; other chat sessions were not accessible through this session's tools.

## Scientific assessment

The environment asks a restricted but real question: which measured gene perturbations should be tested next to recover more published hits within a budget? Each request reveals only prior selected outcomes. It does not test whether an agent can invent an assay, interpret raw instrument data, establish causality, revise a mechanistic explanation, or discover biology outside a finite measured library. Successful transfer would establish improved retrospective experimental selection on these screens. It would be evidence toward the AI scientist thesis, not proof of the whole thesis.

The original repository provides outcome CSVs, published hit arrays and task prompts. We retain hit membership rather than impose a new top-decile objective. Its analysis script's single-gene “hit ratio” is recall of all hits, not precision among tested genes. We report both, cumulative discoveries, enrichment over random, and a per-budget oracle upper bound. [Repository](https://github.com/snap-stanford/BioDiscoveryAgent), [analysis code](https://github.com/snap-stanford/BioDiscoveryAgent/blob/master/analyze.py).

The critical control is corrupted feedback: a later study found that shuffling feedback often barely affected BioDiscoveryAgent's performance. We permute score/hit pairs **within each selected batch**, preserving their joint distribution, and separately hide outcomes while retaining tested IDs. These are feedback-use diagnostics, not standalone proof of learning or its absence. [Gupta et al.](https://arxiv.org/html/2509.21403v1).

Data hygiene is part of the experiment. The inspected Scharenberg CSV has repeated gene IDs and is ordered by score. Preparation defaults to rejecting duplicates; an explicit mean policy records every affected value. Candidates are independently shuffled from a canonical alphabetical order, so input CSV order cannot leak rankings. Published hit membership remains unchanged if duplicates are averaged. This aggregation choice needs review before using Scharenberg as validation. [Inspected table](https://github.com/snap-stanford/BioDiscoveryAgent/blob/master/datasets/ground_truth_Scharenberg22.csv).

## Proposed protocol; freeze before model development

- Split by **study**, not random genes: train on Carnevale and Sanchez (both Sanchez directions together), validate on Scharenberg, finally test on Schmidt IFNG and IL2 together. See `configs/split.json`. This is only two training studies, one validation study and one test study. Seed repetitions do not create new biological studies.
- First audit source publications, preprocessing, candidate coverage, duplicates, score definitions and assay objectives. Verify shared-study assignments and the significance of hit direction before freezing. Do not treat hits as necessarily increased expression.
- Start on training screens. Use five rounds of 128 experiments; use 32 per round on Scharenberg, matching its smaller library. No initial free measured observations. First-round proposals use priors alone. All later results are charged to the budget.
- Use 5 paired seeds for engineering/agent feasibility, then 20 paired seeds per arm for the locked comparison. Temperature-zero models may produce identical repeated runs; report unique trajectories. Shared seeds pair candidate presentation order, not biological replicates.
- Arms: unchanged base model; the same model trained on decision histories; the same model trained on outcomes alone; random; a strong conventional acquisition method. Implemented conventional method: full-covariance ridge Linear-UCB with batch covariance updates. Tune alpha on validation only, using a predeclared small grid (0.1, 0.3, 1, 3), and use the strongest validation setting. A GP baseline can be added if Linear-UCB is weak; do not call a random or gene-hash baseline strong.
- Linear-UCB requires a frozen external feature file: `{ "provenance": { ... }, "vectors": { "GENE": [numbers] } }`. Use outcome-independent biological features, e.g. audited gene embeddings; cover every candidate. Record source, date, dimensionality and exclusion of evaluated screen results. Keep features available to all arms if used for a claim of equal information. The first version sends gene identities and histories to model agents; the optional feature baseline has an explicitly different representation. That comparison is useful as an engineering baseline, but **does not yet establish equal-information superiority**. No biological feature matrix is bundled.
- Run each model arm under true, shuffled and hidden feedback with identical candidate space, tools (initially none), experimental budgets, model context limits, generation limits and retry rules. The same base model and revision must underlie all training arms. Do not grant a trained arm more candidates or a larger context window.
- Invalid, repeated, out-of-library, malformed or overbudget proposals fail a run. There is no silent random fill or unlimited repair. Report completion rate alongside discovery scores; do not exclude failures from the headline comparison. A full campaign-run manager and failure-rate aggregation are still to be added before a large paid sweep.
- Generate teacher trajectories only on training studies. Choose a capable frozen teacher or validated conventional policy, with random exploration for coverage. Do not label trajectories “expert” without evidence. The exporter imitates observed choices; it does not manufacture hidden-outcome-optimal choices or private chain-of-thought explanations.
- Histories and outcomes exports use the same multiset of previously observed measurements in each paired example. The history arm learns the next decision from task, candidate library and measured history; the outcomes arm predicts those same measurements from task and selected IDs. Different objectives and context create token/compute differences. Run a matched-step pilot first, record input and supervised token counts, then a matched-compute sensitivity analysis before attributing any gain specifically to decision history. This is an operational comparison of training packages, not a perfectly isolated causal experiment on one data field.
- With only two training studies, 20 campaigns produce roughly 240 history examples (3 screens × 20 × 4 post-feedback decisions), which are correlated, not independent science problems. Pilot the training effect; do not assume this dataset alone can teach general scientific reasoning.
- Primary endpoint: unique hits at the final fixed budget. Secondary: hit recall, precision, enrichment and cumulative curve. Compare histories minus base and histories minus outcomes within each assay, then check whether true-feedback gains exceed the corresponding shuffled/hidden-feedback gains. Use paired seed bootstrap intervals as conditional uncertainty only. Report IFNG and IL2 separately; one successful assay is not evidence across two independent studies.
- Proposed business continuation rule, to freeze before test access: at least 10% more final discoveries than both unchanged and outcomes-only arms on each held-out assay, positive paired seed intervals, a useful true-feedback advantage, and competitive performance against a tuned conventional optimizer. The 10% is a proposed practical threshold, not a literature-derived law. A failure should identify whether the bottleneck is usable feedback, representation, teacher quality, sample size or training; it does not automatically justify new lab spending.

## Run locally

Try the dependency-free synthetic smoke run from this directory:

```sh
python3 bench.py run --data examples/synthetic.json --rounds 3 --batch 8 --policy external --arm smoke-only --out runs/smoke.json --command python3 examples/random_agent.py
```

This exercises the real process/replay interface, using invented values only.

Python 3.9+ suffices for core replay. NumPy is needed for public `.npy` hit ingestion and Linear-UCB. Create an isolated environment on a network-enabled machine:

```sh
cd experiments/bda
python3 -m venv .venv
.venv/bin/python -m pip install 'numpy>=1.26,<3'
git ls-remote https://github.com/snap-stanford/BioDiscoveryAgent.git refs/heads/master
```

Record the returned full commit SHA, inspect it, and use that immutable revision:

```sh
.venv/bin/python bench.py fetch --revision FULL_40_CHARACTER_COMMIT_SHA
.venv/bin/python bench.py prepare
```

If preparation reports duplicates, review the raw rows before explicitly choosing `--duplicates mean`. If NumPy reports an object array requiring pickle, review the pinned upstream artifact before explicitly adding `--trust-upstream-pickle`; default loading refuses executable pickle payloads. `source_manifest.json` records hashes and URLs; these establish reproducibility, not independent authenticity. Preparation validates the raw-file hashes against that manifest.

Example **training-screen** runs (repeat seeds 0–19 for a locked comparison):

```sh
.venv/bin/python bench.py run --data data/prepared/Carnevale22_Adenosine.json --seed 0 --rounds 5 --batch 128 --policy random --out runs/random_0.json
.venv/bin/python bench.py run --data data/prepared/Carnevale22_Adenosine.json --seed 0 --rounds 5 --batch 128 --policy linear-ucb --features gene_features.json --out runs/ucb_0.json
.venv/bin/python bench.py run --data data/prepared/Carnevale22_Adenosine.json --policy external --arm protocol-demo --out runs/demo_0.json --command .venv/bin/python examples/random_agent.py
```

`--command` must be last. It launches a persistent process that reads one JSON observation per line and writes `{"selected":["GENE", ...]}` per line. The included agent is a protocol demonstration, not an AI. Each campaign gets a fresh process; it should hold no memory between campaigns. The evaluator checks proposals and retains the outcome table. This is **logical information separation, not a security sandbox**: an untrusted local process could read local files. For adversarial agent evaluation, put the agent on a separate host/container with only the protocol stream, no dataset mount or network retrieval tools. Do not mount private truth or logs in its workspace.

```sh
.venv/bin/python bench.py export --runs runs/ucb_0.json --out training/pilot
.venv/bin/python bench.py summarize --runs runs/base_*.json runs/histories_*.json runs/outcomes_*.json --reference base --out runs/comparison.json
python3 -m unittest discover -s tests -v
```

The summary refuses mismatched seed sets and duplicate runs within an arm. Supply matching assay/budget/feedback groups. It does not aggregate biological studies or correct for choosing the best of many trained variants. Freeze the model choice on validation before test evaluation.

## Optional GPU training and model agent

`train_lora.py` provides completion-only QLoRA; `local_model_agent.py` evaluates base or adapter weights using the same protocol. Both require downloaded weights and optional dependencies; neither calls a provider API. These paths are **written but not runtime-tested here**. Model-specific chat templates must have a consistent prompt prefix; incompatible templates fail rather than train on incorrect labels. Package ranges are starting constraints, not a verified lock; save the resolved `pip freeze` and GPU/driver metadata with each run.

On a Linux CUDA host, install `requirements-train.txt`, then run each training arm with the same model revision and settings:

```sh
python train_lora.py --data training/pilot/histories.jsonl --model MODEL_ID --revision MODEL_COMMIT --out adapters/histories --steps 100
python train_lora.py --data training/pilot/outcomes.jsonl --model MODEL_ID --revision MODEL_COMMIT --out adapters/outcomes --steps 100
python bench.py run --data data/prepared/Carnevale22_Adenosine.json --policy external --arm histories --out runs/histories_0.json --command python local_model_agent.py --model MODEL_ID --revision MODEL_COMMIT --adapter adapters/histories
```

For the base arm omit `--adapter`; for outcomes point to the other adapter. Set `--feedback shuffled` / `--feedback hidden` on the evaluator for controls.

**Context feasibility comes before renting a training GPU.** Whole-genome candidate lists can exceed 32k tokens. The code refuses overlength prompts or examples and never truncates the library. Measure the selected tokenizer's actual sequence lengths; choose a compatible long-context model and raise the limits consistently, then profile one forward/backward step. An initially plausible 24–48GB GPU may be inadequate at full-library context; 80GB or more may be needed. No capacity or dollar estimate is asserted without this measurement. Shortlisting would change the benchmark and must be declared as a separate pilot protocol, with identical lists across arms.

These scripts implement the comparison but do not select a base model or claim a successful fine-tune. A useful first milestone is a completed true/shuffled/hidden pilot with a base model that reliably emits valid batches. Full training needs audited public data, features, a chosen model, token profiling and GPU execution. See [PEFT quantized training](https://huggingface.co/docs/peft/main/en/developer_guides/quantization) and [Transformers Trainer](https://huggingface.co/docs/transformers/main/en/main_classes/trainer).

## Verified status, 28 October 2026

- Reviewed upstream dataset layout, task schema, preprocessing example, analysis code and public critique; consulted this workspace's research notes.
- Eleven automated tests pass, and a separate CLI smoke campaign completed through the external-process interface. Core replay and protocol tested on explicitly synthetic fixtures. Synthetic values say nothing about biological capability.
- Shell network fetch failed with DNS resolution errors. Public datasets have **not** been downloaded, cleaned or benchmarked locally. No scientific result is reported.
- NumPy, Torch and Transformers are absent in the current Python environment. Linear-UCB numerical execution and optional GPU training/inference are not verified here.
- No paid calls, GPU rentals, laboratory orders or weight training occurred.

CEO note: We can cheaply test whether an AI actually changes its next experiment when nature answers. That is a valuable first milestone. The prize is transfer to an unfamiliar study; a prettier prediction curve or more plausible explanation is not enough. I would spend on this pilot before buying laboratory data.

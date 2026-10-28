"""Retrospective perturbation benchmark. Core replay uses Python's standard library."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import re
import statistics
import subprocess
import sys
import time
import urllib.request

DATASETS = ['IFNG', 'IL2', 'Carnevale22_Adenosine', 'Scharenberg22', 'Sanchez21', 'Sanchez21_down']
ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def load_json(path):
    return json.loads(Path(path).read_text())


def fetch(args):
    # Require an immutable revision; never silently follow master.
    if not re.fullmatch(r'[0-9a-f]{40}', args.revision):
        raise ValueError('--revision must be a full 40-character Git commit SHA')
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    manifest = {'repository': 'https://github.com/snap-stanford/BioDiscoveryAgent',
                'revision': args.revision, 'files': {}}
    for name in DATASETS:
        for file in [f'ground_truth_{name}.csv', f'topmovers_{name}.npy', f'task_prompts/{name}.json']:
            url = f'https://raw.githubusercontent.com/snap-stanford/BioDiscoveryAgent/{args.revision}/datasets/{file}'
            path = dest / file
            path.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
            temporary = path.with_suffix(path.suffix + '.part')
            temporary.write_bytes(data)
            temporary.replace(path)
            manifest['files'][file] = {'url': url, 'sha256': digest(path)}
            write_json(dest / 'source_manifest.json', manifest)
    print(f'Downloaded {len(manifest["files"])} files to {dest}')


def prepare_csv(path, hits, name, task, duplicate_policy='error'):
    """Use published hit membership, not a new percentile threshold."""
    grouped = {}
    with open(path, newline='') as handle:
        reader = csv.DictReader(handle)
        if 'Gene' not in (reader.fieldnames or []):
            raise ValueError('Missing Gene column')
        score_cols = [c for c in reader.fieldnames if c != 'Gene' and not c.startswith('Unnamed:')]
        if len(score_cols) != 1:
            raise ValueError(f'Ambiguous score columns: {score_cols}')
        for row in reader:
            gene = row['Gene'].strip()
            score = float(row[score_cols[0]])
            if not gene or not math.isfinite(score):
                raise ValueError('Empty gene or non-finite outcome')
            grouped.setdefault(gene, []).append(score)
    duplicates = {g: v for g, v in grouped.items() if len(v) > 1}
    if duplicates and duplicate_policy == 'error':
        raise ValueError(f'{len(duplicates)} duplicate genes; review and use --duplicates mean explicitly')
    unknown = set(hits) - set(grouped)
    if unknown:
        raise ValueError(f'{len(unknown)} published hits absent from measured candidates')
    rows = [{'id': g, 'score': statistics.mean(grouped[g]), 'hit': g in hits} for g in sorted(grouped)]
    if not rows or not 0 < sum(r['hit'] for r in rows) < len(rows):
        raise ValueError('Need both hit and non-hit candidates')
    return {'schema': 1, 'dataset': name, 'task': task, 'rows': rows,
            'provenance': {'csv_sha256': digest(path), 'duplicate_policy': duplicate_policy,
                           'duplicates': duplicates, 'score_column': score_cols[0]}}


def prepare(args):
    import numpy as np  # Only ingestion and the linear baseline need NumPy.
    source = Path(args.source)
    manifest = load_json(source / 'source_manifest.json')
    # Verify every raw artifact before processing.
    for file, meta in manifest['files'].items():
        if digest(source / file) != meta['sha256']:
            raise ValueError(f'Raw artifact changed: {file}')
    for name in DATASETS:
        hp = source / f'topmovers_{name}.npy'
        # Object arrays may contain executable pickle payloads. Default refuses them.
        hits = np.load(hp, allow_pickle=args.trust_upstream_pickle).tolist()
        if not isinstance(hits, list) or not all(isinstance(x, str) for x in hits):
            raise ValueError('Expected a flat string hit array')
        data = prepare_csv(source / f'ground_truth_{name}.csv', set(hits), name,
                           load_json(source / 'task_prompts' / f'{name}.json'), args.duplicates)
        data['provenance'].update({'source': manifest, 'hits_sha256': digest(hp)})
        write_json(Path(args.out) / f'{name}.json', data)
    print(f'Prepared datasets in {args.out}')


def validate_dataset(data):
    rows = data['rows']
    ids = [r['id'] for r in rows]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError('Candidate IDs must be nonempty and unique')
    for row in rows:
        if not isinstance(row['id'], str) or not row['id'] or type(row['hit']) is not bool or not math.isfinite(row['score']):
            raise ValueError('Invalid candidate record')
    if not 0 < sum(r['hit'] for r in rows) < len(rows):
        raise ValueError('Need both hits and non-hits')


def observation(task, candidates, history, batch, round_no, seed):
    return {'task': task, 'candidates': candidates, 'history': history,
            'batch_size': batch, 'round': round_no, 'seed': seed,
            'instruction': 'Select exactly batch_size distinct untested candidate IDs. Return JSON {"selected": [IDs]}. Maximize total discovered hits.'}


def check_selection(selected, candidates, batch):
    if not isinstance(selected, list) or len(selected) != batch or not all(isinstance(x, str) for x in selected):
        raise ValueError('Agent must return exactly batch_size string IDs')
    if len(set(selected)) != batch or not set(selected) <= set(candidates):
        raise ValueError('Repeated, already tested, or out-of-library selection; run invalid, no random repair')


class RandomPolicy:
    def __init__(self, seed):
        self.rng = random.Random(seed)

    def select(self, obs):
        return self.rng.sample(obs['candidates'], obs['batch_size'])


class ExternalPolicy:
    """A persistent JSON-lines process sees public observations only, never evaluator paths."""
    def __init__(self, command):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=sys.stderr, text=True, bufsize=1)

    def select(self, obs):
        import selectors
        self.process.stdin.write(json.dumps(obs) + '\n')
        self.process.stdin.flush()
        selector = selectors.DefaultSelector()
        try:
            selector.register(self.process.stdout, selectors.EVENT_READ)
            if not selector.select(timeout=600):
                raise TimeoutError('External agent exceeded 600 seconds')
            return json.loads(self.process.stdout.readline())['selected']
        finally:
            selector.close()

    def close(self):
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process.stdin.close()
        self.process.stdout.close()


class LinearUCB:
    """Full covariance ridge UCB on audited, outcome-independent gene features.

    Batch uses one posterior and sequential covariance-only updates to avoid redundancy.
    """
    def __init__(self, features, alpha=1.0):
        import numpy as np
        self.np, self.features, self.alpha = np, features, alpha
        dims = {len(v) for v in features.values()}
        if len(dims) != 1 or not next(iter(dims)):
            raise ValueError('Features need one nonempty shared dimension')
        if not all(all(math.isfinite(x) for x in v) for v in features.values()):
            raise ValueError('Non-finite feature')

    def select(self, obs):
        np = self.np
        # L2 normalization uses no labels and is identical across tasks.
        def vector(g):
            x = np.array(self.features[g], dtype=float)
            return np.concatenate(([1.0], x / max(float(np.linalg.norm(x)), 1e-12)))
        ids = obs['candidates']
        X = np.array([vector(g) for g in ids])
        inv = np.eye(X.shape[1])
        b = np.zeros(X.shape[1])
        for event in obs['history']:
            if event['feedback'] is None:
                continue
            for result in event['feedback']:
                x = vector(result['id'])
                v = inv @ x
                inv -= np.outer(v, v) / (1 + x @ v)
                b += x * float(result['hit'])
        mean = X @ (inv @ b)
        chosen = []
        for _ in range(obs['batch_size']):
            variance = np.maximum(np.sum((X @ inv) * X, axis=1), 0)
            scores = mean + self.alpha * np.sqrt(variance)
            scores[chosen] = -np.inf
            index = int(np.argmax(scores))
            chosen.append(index)
            x = X[index]
            v = inv @ x
            inv -= np.outer(v, v) / (1 + x @ v)
        return [ids[i] for i in chosen]


def replay(data, policy, seed=0, rounds=5, batch=128, feedback='true'):
    validate_dataset(data)
    if rounds < 1 or batch < 1 or rounds * batch > len(data['rows']):
        raise ValueError('Positive rounds/batch required and budget cannot exceed measured library')
    if feedback not in ('true', 'shuffled', 'hidden'):
        raise ValueError('Unknown feedback mode')
    oracle = {r['id']: r for r in data['rows']}
    candidates = sorted(oracle)
    # Never expose source row order: source CSVs can be ranked by outcome.
    random.Random(seed).shuffle(candidates)
    shuffle_rng = random.Random(seed + 1000003)
    history, events, metrics = [], [], []
    total_hits = sum(r['hit'] for r in oracle.values())
    hits = 0
    started = time.monotonic()
    for r in range(1, rounds + 1):
        obs = observation(data['task'], candidates[:], history[:], batch, r, seed)
        # JSON round-trip makes observation and oracle ownership explicit.
        public = json.loads(json.dumps(obs))
        selected = policy.select(public)
        check_selection(selected, candidates, batch)
        truth = [dict(oracle[g]) for g in selected]
        hits += sum(x['hit'] for x in truth)
        if feedback == 'hidden':
            shown = None
        else:
            values = [(x['score'], x['hit']) for x in truth]
            if feedback == 'shuffled':
                shuffle_rng.shuffle(values)  # preserve joint score/hit distribution within batch
            shown = [{'id': g, 'score': v[0], 'hit': v[1]} for g, v in zip(selected, values)]
        history.append({'round': r, 'selected': selected[:], 'feedback': shown})
        events.append({'observation': obs, 'selected': selected[:], 'truth': truth})
        picked = set(selected)
        candidates = [g for g in candidates if g not in picked]
        n = r * batch
        metrics.append({'round': r, 'experiments': n, 'hits': hits,
                        'hit_recall': hits / total_hits, 'precision': hits / n,
                        'enrichment': (hits / n) / (total_hits / len(oracle)),
                        'oracle_hits': min(n, total_hits)})
    return {'schema': 1, 'dataset': data['dataset'], 'seed': seed, 'feedback': feedback,
            'rounds': rounds, 'batch': batch, 'candidate_count': len(oracle),
            'total_hits': total_hits, 'metrics': metrics, 'events': events,
            'elapsed_seconds': time.monotonic() - started}


def run(args):
    data = load_json(args.data)
    if args.policy == 'external':
        if not args.command:
            raise ValueError('Supply --command followed by executable and arguments')
        policy = ExternalPolicy(args.command)
    elif args.policy == 'linear-ucb':
        if not args.features:
            raise ValueError('Linear-UCB requires --features; gene-name hashes are not valid biology features')
        features = load_json(args.features)
        if not features.get('provenance'):
            raise ValueError('Feature provenance is required')
        if not set(r['id'] for r in data['rows']) <= set(features['vectors']):
            raise ValueError('Features must cover every candidate')
        policy = LinearUCB(features['vectors'], args.alpha)
    else:
        policy = RandomPolicy(args.seed)
    try:
        result = replay(data, policy, args.seed, args.rounds, args.batch, args.feedback)
    finally:
        if hasattr(policy, 'close'):
            policy.close()
    result.update({'arm': args.arm or args.policy, 'policy': args.policy,
                   'data_sha256': digest(args.data), 'code_sha256': digest(__file__),
                   'features_sha256': digest(args.features) if args.features else None,
                   'command': args.command, 'alpha': args.alpha})
    write_json(args.out, result)
    print(json.dumps(result['metrics'][-1], indent=2))


def export(args):
    split = load_json(args.split)
    allowed = set(split['train'])
    histories, outcomes = [], []
    for path in args.runs:
        run = load_json(path)
        if run['dataset'] not in allowed or run['feedback'] != 'true':
            raise ValueError(f'Training export refused for {path}: not train split with true feedback')
        for event in run['events']:
            if not event['observation']['history']:
                continue  # no measured data exists before round one
            prior_results = [result for h in event['observation']['history'] for result in h['feedback']]
            common = {'dataset': run['dataset'], 'seed': run['seed'], 'run_sha256': digest(path)}
            histories.append(dict(common, messages=[
                {'role': 'user', 'content': json.dumps(event['observation'])},
                {'role': 'assistant', 'content': json.dumps({'selected': event['selected']})}]))
            # Exactly the same measured outcomes, without the sequential context.
            outcomes.append(dict(common, messages=[
                {'role': 'user', 'content': json.dumps({'task': event['observation']['task'],
                 'instruction': 'Predict the score and hit label for each candidate.', 'candidates': [r['id'] for r in prior_results]})},
                {'role': 'assistant', 'content': json.dumps({'results': prior_results})}]))
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    for name, records in [('histories', histories), ('outcomes', outcomes)]:
        (dest / f'{name}.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in records))
    write_json(dest / 'manifest.json', {'split': split, 'source_runs': [digest(p) for p in args.runs],
                                      'examples_per_arm': len(histories),
                                      'warning': 'Teacher imitation targets, not proof of optimal actions. Token exposures differ; report training tokens.'})
    print(f'Exported {len(histories)} examples per arm')


def summarize(args):
    groups = {}
    for path in args.runs:
        run = load_json(path)
        key = (run['dataset'], run['feedback'], run['rounds'], run['batch'], run['data_sha256'])
        arm = run['arm']
        slot = groups.setdefault(key, {}).setdefault(arm, {})
        if run['seed'] in slot:
            raise ValueError('Duplicate dataset/arm/feedback/seed')
        slot[run['seed']] = run['metrics'][-1]['hits']
    report = []
    rng = random.Random(0)
    # Pairing on seed reduces order variance; seeds are not independent biological studies.
    for key, arms in groups.items():
        if args.reference not in arms or len(arms) < 2:
            raise ValueError('Every comparison group needs the reference and at least one other arm; check dataset hashes, budgets and feedback modes')
        ref = arms[args.reference]
        for arm, values in arms.items():
            if set(ref) != set(values):
                raise ValueError('All compared arms must have exactly the same seeds')
            deltas = [values[s] - ref[s] for s in sorted(ref)]
            boots = sorted(statistics.mean(rng.choices(deltas, k=len(deltas))) for _ in range(5000))
            report.append({'dataset': key[0], 'feedback': key[1], 'arm': arm, 'reference': args.reference,
                           'seeds': len(deltas), 'mean_hits': statistics.mean(values.values()),
                           'mean_delta_hits': statistics.mean(deltas), 'paired_seed_bootstrap_95': [boots[124], boots[4874]],
                           'warning': 'Conditional seed variability only; not uncertainty across biological studies.'})
    if not report:
        raise ValueError('No compatible comparisons with reference arm')
    write_json(args.out, report)
    print(json.dumps(report, indent=2))


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation', required=True)
    f = sub.add_parser('fetch'); f.add_argument('--revision', required=True); f.add_argument('--out', default=str(ROOT / 'data/raw')); f.set_defaults(func=fetch)
    f = sub.add_parser('prepare'); f.add_argument('--source', default=str(ROOT / 'data/raw')); f.add_argument('--out', default=str(ROOT / 'data/prepared')); f.add_argument('--duplicates', choices=['error', 'mean'], default='error'); f.add_argument('--trust-upstream-pickle', action='store_true'); f.set_defaults(func=prepare)
    f = sub.add_parser('run'); f.add_argument('--data', required=True); f.add_argument('--policy', choices=['random', 'linear-ucb', 'external'], default='random'); f.add_argument('--arm'); f.add_argument('--seed', type=int, default=0); f.add_argument('--rounds', type=int, default=5); f.add_argument('--batch', type=int, default=128); f.add_argument('--feedback', choices=['true', 'shuffled', 'hidden'], default='true'); f.add_argument('--features'); f.add_argument('--alpha', type=float, default=1.0); f.add_argument('--out', required=True); f.add_argument('--command', nargs=argparse.REMAINDER); f.set_defaults(func=run)
    f = sub.add_parser('export'); f.add_argument('--split', default=str(ROOT / 'configs/split.json')); f.add_argument('--runs', nargs='+', required=True); f.add_argument('--out', required=True); f.set_defaults(func=export)
    f = sub.add_parser('summarize'); f.add_argument('--runs', nargs='+', required=True); f.add_argument('--reference', required=True); f.add_argument('--out', required=True); f.set_defaults(func=summarize)
    return p


if __name__ == '__main__':
    parser_args = parser().parse_args()
    parser_args.func(parser_args)

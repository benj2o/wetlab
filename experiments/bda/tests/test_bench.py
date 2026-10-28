import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bench


def fixture():
    return {'schema': 1, 'dataset': 'Carnevale22_Adenosine', 'task': {'Task': 'synthetic engineering fixture'},
            'rows': [{'id': f'G{i:03}', 'score': float(i), 'hit': i >= 24} for i in range(40)]}


class ReplayTests(unittest.TestCase):
    def test_no_hidden_outcomes_or_rank_order(self):
        data = fixture()
        class Spy:
            def select(self, obs):
                if obs['round'] == 1:
                    self.first = obs['candidates'][:]
                    self.obs = copy.deepcopy(obs)
                return obs['candidates'][:obs['batch_size']]
        spy = Spy()
        bench.replay(data, spy, rounds=3, batch=4)
        self.assertEqual(spy.obs['history'], [])
        self.assertNotIn('rows', spy.obs)
        self.assertNotEqual(spy.first, [r['id'] for r in data['rows']])
        reverse = copy.deepcopy(data); reverse['rows'].reverse()
        other = Spy(); bench.replay(reverse, other, rounds=3, batch=4)
        self.assertEqual(spy.first, other.first)

    def test_feedback_controls_preserve_oracle_scoring(self):
        results = [bench.replay(fixture(), bench.RandomPolicy(3), seed=3, rounds=3, batch=8, feedback=m)
                   for m in ['true', 'shuffled', 'hidden']]
        self.assertEqual(results[0]['metrics'], results[1]['metrics'])
        self.assertEqual(results[0]['metrics'], results[2]['metrics'])
        a, b = results[:2]
        truth = a['events'][1]['observation']['history'][0]['feedback']
        shuffled = b['events'][1]['observation']['history'][0]['feedback']
        self.assertEqual(sorted((x['score'], x['hit']) for x in truth), sorted((x['score'], x['hit']) for x in shuffled))
        self.assertNotEqual(truth, shuffled)
        self.assertIsNone(results[2]['events'][1]['observation']['history'][0]['feedback'])

    def test_repeatable_unique_fixed_budget(self):
        a = bench.replay(fixture(), bench.RandomPolicy(7), rounds=5, batch=8)
        b = bench.replay(fixture(), bench.RandomPolicy(7), rounds=5, batch=8)
        self.assertEqual(a['metrics'], b['metrics'])
        chosen = [g for e in a['events'] for g in e['selected']]
        self.assertEqual(len(set(chosen)), 40)
        self.assertEqual(a['metrics'][-1]['hit_recall'], 1)
        self.assertEqual(a['metrics'][-1]['enrichment'], 1)

    def test_invalid_selection_fails_without_free_repair(self):
        for selected in [['G001', 'G001'], ['NO', 'G001'], ['G001'], 'G001']:
            with self.assertRaises(ValueError):
                bench.check_selection(selected, ['G001', 'G002'], 2)

    def test_overbudget(self):
        with self.assertRaises(ValueError):
            bench.replay(fixture(), bench.RandomPolicy(0), rounds=6, batch=8)

    def test_policy_mutation_cannot_change_oracle(self):
        class Mutator:
            def select(self, obs):
                picked = obs['candidates'][:2]
                obs['history'].clear(); obs['candidates'].clear()
                return picked
        run = bench.replay(fixture(), Mutator(), rounds=3, batch=2)
        self.assertEqual(len(run['events'][2]['observation']['history']), 2)

    def test_process_protocol(self):
        policy = bench.ExternalPolicy([sys.executable, str(bench.ROOT / 'examples/random_agent.py')])
        try:
            external = bench.replay(fixture(), policy, rounds=2, batch=4)
        finally:
            policy.close()
        local = bench.replay(fixture(), bench.RandomPolicy(0), rounds=2, batch=4)
        self.assertEqual(external['metrics'], local['metrics'])

    def test_duplicate_and_nonfinite_outcomes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'raw.csv'
            path.write_text('Gene,Score\nA,1\nA,3\nB,0\n')
            with self.assertRaises(ValueError):
                bench.prepare_csv(path, {'A'}, 'test', {})
            data = bench.prepare_csv(path, {'A'}, 'test', {}, 'mean')
            self.assertEqual(data['rows'][0]['score'], 2)
            path.write_text('Gene,Score\nA,nan\nB,0\n')
            with self.assertRaises(ValueError):
                bench.prepare_csv(path, {'A'}, 'test', {})

    def test_training_exports_refuse_test_and_match_outcome_exposures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = bench.replay(fixture(), bench.RandomPolicy(0), rounds=3, batch=4)
            rp = root / 'run.json'; bench.write_json(rp, run)
            args = SimpleNamespace(split=bench.ROOT / 'configs/split.json', runs=[rp], out=root / 'export')
            bench.export(args)
            hist = [json.loads(l) for l in (root / 'export/histories.jsonl').read_text().splitlines()]
            outs = [json.loads(l) for l in (root / 'export/outcomes.jsonl').read_text().splitlines()]
            self.assertEqual(len(hist), 2)
            for h, o in zip(hist, outs):
                obs = json.loads(h['messages'][0]['content'])
                exposed = [x for event in obs['history'] for x in event['feedback']]
                self.assertEqual(exposed, json.loads(o['messages'][1]['content'])['results'])
            run['dataset'] = 'IFNG'; bench.write_json(rp, run)
            with self.assertRaises(ValueError):
                bench.export(args)


class SummaryTests(unittest.TestCase):
    def test_paired_analysis_and_duplicate_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for arm in ['base', 'trained']:
                for seed in range(3):
                    run = bench.replay(fixture(), bench.RandomPolicy(seed), seed=seed, rounds=2, batch=4)
                    run.update(arm=arm, data_sha256='same')
                    path = root / f'{arm}{seed}.json'
                    bench.write_json(path, run); paths.append(path)
            args = SimpleNamespace(runs=paths, reference='base', out=root / 'summary.json')
            bench.summarize(args)
            report = bench.load_json(args.out)
            self.assertTrue(all(r['mean_delta_hits'] == 0 for r in report))
            args.runs = paths + paths[:1]
            with self.assertRaises(ValueError):
                bench.summarize(args)

    def test_missing_seed_or_incompatible_budget_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for arm, rounds in [('base', 2), ('trained', 3)]:
                run = bench.replay(fixture(), bench.RandomPolicy(0), rounds=rounds, batch=4)
                run.update(arm=arm, data_sha256='same')
                path = root / f'{arm}.json'; bench.write_json(path, run); paths.append(path)
            with self.assertRaises(ValueError):
                bench.summarize(SimpleNamespace(runs=paths, reference='base', out=root / 'summary.json'))


if __name__ == '__main__':
    unittest.main()

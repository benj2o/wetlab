"""Protocol demonstration, NOT an LLM agent. One persistent process per campaign."""
import json
import random
import sys
rng = None
for line in sys.stdin:
    obs = json.loads(line)
    if rng is None:
        rng = random.Random(obs['seed'])
    print(json.dumps({'selected': rng.sample(obs['candidates'], obs['batch_size'])}), flush=True)

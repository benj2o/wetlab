"""Optional persistent Transformers agent, base or LoRA adapter; no hosted API.

stdout is reserved for JSON-lines. Unparseable/invalid selections fail the run.
No automatic retries, random fillers, hidden-outcome access, or silent context truncation.
"""
import argparse
import json
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True); p.add_argument('--revision', required=True)
    p.add_argument('--adapter'); p.add_argument('--max-input-tokens', type=int, default=32768)
    p.add_argument('--max-new-tokens', type=int, default=4096)
    a = p.parse_args()
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
    from peft import PeftModel
    tokenizer = AutoTokenizer.from_pretrained(a.model, revision=a.revision, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(a.model, revision=a.revision, trust_remote_code=False,
                                               device_map='auto', torch_dtype='auto')
    if a.adapter:
        model = PeftModel.from_pretrained(model, a.adapter)
    model.eval()
    for line in sys.stdin:
        obs = json.loads(line)
        set_seed(obs['seed'])
        messages = [{'role': 'user', 'content': json.dumps(obs)}]
        ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors='pt')
        if ids.shape[1] > a.max_input_tokens:
            raise ValueError(f'Prompt has {ids.shape[1]} tokens; limit is {a.max_input_tokens}. Choose a compatible context length; do not truncate the candidate library.')
        with torch.inference_mode():
            generated = model.generate(ids.to(model.device), max_new_tokens=a.max_new_tokens,
                                       do_sample=False, pad_token_id=tokenizer.eos_token_id)
        text = tokenizer.decode(generated[0, ids.shape[1]:], skip_special_tokens=True).strip()
        # JSON only is the contract for every training/evaluation arm.
        result = json.loads(text)
        print(json.dumps({'selected': result['selected']}), flush=True)


if __name__ == '__main__':
    main()

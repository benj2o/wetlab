"""Optional CUDA QLoRA training. No provider API. Install requirements-train.txt.

Completion-only loss; reject overlength examples rather than truncating experimental history.
Run separate jobs with identical base revision, seed, steps, and sequence limits for each arm.
"""
import argparse
import json
from pathlib import Path
import hashlib


def encode_example(tokenizer, messages, max_length):
    prompt = tokenizer.apply_chat_template(messages[:-1], tokenize=True, add_generation_prompt=True)
    full = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=False)
    if full[:len(prompt)] != prompt:
        raise ValueError('Chat template prefix mismatch; select a compatible template')
    if len(full) > max_length:
        raise ValueError(f'Example is {len(full)} tokens, over {max_length}; no silent truncation')
    return {'input_ids': full, 'attention_mask': [1] * len(full),
            'labels': [-100] * len(prompt) + full[len(prompt):]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', required=True); p.add_argument('--model', required=True)
    p.add_argument('--revision', required=True); p.add_argument('--out', required=True)
    p.add_argument('--steps', type=int, default=100); p.add_argument('--max-length', type=int, default=32768)
    p.add_argument('--seed', type=int, default=0)
    a = p.parse_args()
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, Trainer, TrainingArguments, set_seed
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    if not torch.cuda.is_available():
        raise RuntimeError('This optional trainer requires a CUDA GPU; core evaluation does not')
    set_seed(a.seed)
    tokenizer = AutoTokenizer.from_pretrained(a.model, revision=a.revision, trust_remote_code=False)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    examples = [encode_example(tokenizer, json.loads(line)['messages'], a.max_length)
                for line in Path(a.data).read_text().splitlines() if line.strip()]
    if not examples:
        raise ValueError('No training examples')
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForCausalLM.from_pretrained(a.model, revision=a.revision, trust_remote_code=False,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=dtype), device_map={'': 0})
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                                           target_modules='all-linear', task_type='CAUSAL_LM'))
    model.config.use_cache = False
    def collate(rows):
        n = max(len(r['input_ids']) for r in rows)
        return {k: torch.tensor([r[k] + [(-100 if k == 'labels' else tokenizer.pad_token_id if k == 'input_ids' else 0)] * (n - len(r[k])) for r in rows])
                for k in ['input_ids', 'attention_mask', 'labels']}
    args = TrainingArguments(output_dir=a.out, max_steps=a.steps, per_device_train_batch_size=1,
        gradient_accumulation_steps=8, learning_rate=2e-4, bf16=dtype == torch.bfloat16,
        fp16=dtype == torch.float16, gradient_checkpointing=True, report_to='none',
        save_strategy='no', logging_steps=10, seed=a.seed, remove_unused_columns=False)
    trainer = Trainer(model=model, args=args, train_dataset=examples, data_collator=collate)
    trainer.train()
    trainer.save_model(a.out); tokenizer.save_pretrained(a.out)
    Path(a.out, 'training_manifest.json').write_text(json.dumps(dict(vars(a),
        data_sha256=hashlib.sha256(Path(a.data).read_bytes()).hexdigest(), examples=len(examples),
        total_input_tokens=sum(len(e['input_ids']) for e in examples),
        total_supervised_tokens=sum(sum(x != -100 for x in e['labels']) for e in examples)), indent=2))


if __name__ == '__main__':
    main()

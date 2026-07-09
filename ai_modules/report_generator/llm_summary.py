"""
Loads the LLM once and exposes generate_report_text(). Adapted from
notebook cells 2-3.
 
IMPORTANT: loading a 7B model per-request is not viable inside a FastAPI
request/response cycle. The model is loaded lazily on first call and cached
for the life of the process (see @lru_cache below). This also requires a
GPU with ~16GB+ VRAM for fp16 inference.
 
If that's not available in your deployment environment, swap _load_pipeline()
and generate_report_text() for an API-based LLM call instead (e.g. Anthropic
or OpenAI) — keep the same function signature so report.py doesn't need to
change.
"""
import logging
from functools import lru_cache
 
logger = logging.getLogger(__name__)
 
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
 
SYSTEM_PROMPT = """
You are a Senior Business Intelligence Consultant.
 
Write executive reports in McKinsey/BCG consulting style.
 
Rules:
- No repetition of KPI tables
- No generic filler sentences
- Deep interpretation only
- Structured sections with clear headings
- Always complete the report fully
- Be concise but insightful
"""
 
 
@lru_cache(maxsize=1)
def _load_pipeline():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
 
    logger.info("Loading %s ... this can take a while on first call", MODEL_ID)
 
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return tokenizer, pipe
 
 
def generate_report_text(prompt: str) -> str:
    """Runs the LLM on a fully-built KPI prompt, returns the narrative text."""
    tokenizer, pipe = _load_pipeline()
 
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
 
    output = pipe(
        text,
        max_new_tokens=1200,
        do_sample=False,
        temperature=0.3,
        top_p=0.9,
        repetition_penalty=1.1,
        return_full_text=False,
    )
    return output[0]["generated_text"]
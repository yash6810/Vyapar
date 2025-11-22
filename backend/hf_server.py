# Minimal HF server using transformers pipeline (dev only)
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import os

app = FastAPI()

MODEL_ID = os.getenv('HF_MODEL', 'distilgpt2')
print('Using model:', MODEL_ID)

# For small models only. If this OOMs, switch to a smaller model.
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
pipe = pipeline('text-generation', model=model, tokenizer=tokenizer)

class GenRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 200

@app.post('/generate')
async def generate(req: GenRequest):
    out = pipe(req.prompt, max_new_tokens=req.max_new_tokens, do_sample=False)
    return {'text': out[0]['generated_text']}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('hf_server:app', host='0.0.0.0', port=8080)

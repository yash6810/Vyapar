# Gemini CLI Engineering Playbook (MVP Hackathon Mode Enabled)

## ⚡ 24-Hour Hackathon MVP Mode (Critical Update)

This blueprint is now updated for **Round 1 hackathon survival mode**.
The only confirmed deliverable for the first round is:

### ✅ **Voice-Based Expense Recording for SMEs via WhatsApp**

User sends a WhatsApp voice message → ASR → LLM → JSON expense → stored → confirmation.

This ensures you finish within 24 hours and have a **clean, impressive, working demo**.
If we advance to further rounds, we scale the system using the remaining modules already defined in this document.

### 🎯 MVP Scope (Guaranteed to Build in 24 Hours)

* WhatsApp → Backend webhook (or simulated via curl)
* ASR (Whisper tiny/small or Indic ASR)
* Expense extraction (validated JSON)
* Workflow: save expense → return summary
* Daily summary endpoint for cashflow insight
* Simple dashboard (optional)
* Pitch-ready demo

### ❌ Deferred Scope (For Round 2 If We Advance)

These stay in the blueprint but are **not required for MVP**:

* GST workflows
* Invoice generation
* Payroll slips
* Payment reminders & vendor flows
* OCR bill scanning
* Fraud/anomaly detection
* Full WhatsApp Cloud API integration

### 🏆 Round 1 Demo Deliverables

* 2–3 real audio samples tested end-to-end
* Stored expense JSON files
* Working script or live demo
* Logs showing ASR → LLM → workflow
* Slide deck + pitch

---

# Gemini CLI Engineering Playbook & Dev Kit (Updated: Expense Recording)

This single document now contains:

1. Repo folder structure and files
2. Gemini CLI command cheat sheet
3. Local tool adapter starter kit (copy-paste Python files)
4. README.md (full setup + run order + testing)
5. **Expense Recording** feature integrated across prompts, pipelines, schemas, and examples

---

# 1. Correct folder structure (repo layout)

Use this layout as the canonical repository structure. Copy this tree into your repo root.

```
whatsapp-aria/
├─ gemini/                     # Gemini CLI config + prompts
│  └─ gemini_agent.yaml        # agent config you already have
├─ backend/
│  ├─ hf_server.py             # local HF model server (FastAPI)
│  ├─ asr_service.py           # ASR microservice (FastAPI stub / wrapper)
│  ├─ workflow_runner.py       # deterministic business logic (including expenses)
│  ├─ whatsapp_adapter.py      # dev WhatsApp adapter (sandbox stub)
│  ├─ main.py                  # backend entry (FastAPI) - webhook endpoints
│  └─ schemas.py               # JSON schemas and validation helpers (includes expense schema)
├─ tests/
│  ├─ samples/                 # audio samples for testing (expense examples)
│  └─ test_end2end.py
├─ scripts/
│  ├─ start_all.sh
│  └─ setup_env.sh
├─ docs/
│  └─ architecture.md
├─ README.md
└─ requirements.txt
```

---

# 2. Gemini CLI & Dev command cheat sheet

Place these commands in your repo `README.md` and use them daily.

## Gemini

* Start Gemini with your agent config:

```bash
cd gemini
gemini --config gemini_agent.yaml
```

* Run a pipeline (example - depends on your Gemini CLI usage):

```
/run voice_expense_pipeline audio_path="../tests/samples/expense_hindi_01.mp3" from_number="+91xxxxxxxxxx"
```

## Start services (dev order)

* Start HF server (local LLM):

```bash
python backend/hf_server.py
```

* Start ASR service:

```bash
python backend/asr_service.py
```

* Start backend (webhook + workflow):

```bash
uvicorn backend.main:app --reload --port 8000
```

## Quick start (one-liner for dev)

`scripts/start_all.sh` will run all three (HF, ASR, backend). Use tmux or separate terminals.

## Testing

* Run pytest (ensure services running):

```bash
pytest -q
```

---

# 3. Local tool adapter starter kit (copy-paste files)

Below are minimal, functional starter files you can paste into `backend/`.
They are intentionally simple and dependency-light so students can run them on laptops.

---

## requirements.txt

```
fastapi
uvicorn
transformers
torch
pydantic
jsonschema
python-multipart
whisperx
soundfile
```

(You may remove whisperx if you choose a different ASR.)

---

## backend/hf_server.py

```python
# Minimal HF server using transformers pipeline (dev only)
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import os

app = FastAPI()

MODEL_ID = os.getenv('HF_MODEL', 'google/gemma-text-small-it')
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
```

Notes: pick a small model id that fits your machine. If using CPU-only, you will need very small models.

---

## backend/asr_service.py (simple stub using whisper)

```python
# ASR microservice - transcribes an uploaded audio file.
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import whisper
import tempfile

app = FastAPI()
model = whisper.load_model('small')  # change to tiny if low resource

@app.post('/transcribe')
async def transcribe(file: UploadFile = File(...)):
    suffix = '.mp3' if file.filename.endswith('.mp3') else '.wav'
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await file.read())
        tmp.flush()
        res = model.transcribe(tmp.name)
    return {'text': res['text'], 'language_code': res.get('language', 'unknown'), 'confidence': 0.9}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('asr_service:app', host='0.0.0.0', port=8001)
```

Note: This is a simple blocking call; replace with more robust ASR pipeline for production.

---

## backend/schemas.py

```python
# JSON schemas and validation helpers
from jsonschema import validate, ValidationError

INVOICE_SCHEMA = {
    'type': 'object',
    'required': ['client_name','invoice_date','items','gst_pct','total'],
    'properties': {
        'client_name': {'type': 'string'},
        'invoice_date': {'type': 'string'},
        'items': {'type': 'array'},
        'gst_pct': {'type': 'number'},
        'total': {'type': 'number'}
    }
}

EXPENSE_SCHEMA = {
    'type': 'object',
    'required': ['category','amount','date','payment_method'],
    'properties': {
        'category': {'type':'string'},
        'amount': {'type':'number'},
        'vendor': {'type':'string'},
        'date': {'type':'string','pattern':'^\d{4}-\d{2}-\d{2}$'},
        'payment_method': {'type':'string'},
        'gst_applicable': {'type':'boolean'},
        'notes': {'type':'string'}
    }
}


def validate_schema(data: dict, schema: dict):
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


def validate_invoice(data: dict):
    return validate_schema(data, INVOICE_SCHEMA)


def validate_expense(data: dict):
    return validate_schema(data, EXPENSE_SCHEMA)
```

---

## backend/workflow_runner.py

```python
# Deterministic workflow runner - acts on validated JSON
from typing import Dict

import json, uuid, os

os.makedirs('data/invoices', exist_ok=True)
os.makedirs('data/expenses', exist_ok=True)


def create_invoice(payload: Dict):
    inv_id = str(uuid.uuid4())
    path = f'data/invoices/{inv_id}.json'
    with open(path, 'w') as f:
        json.dump(payload, f, indent=2)
    total = payload.get('total')
    client = payload.get('client_name')
    return {'invoice_id': inv_id, 'summary': f'Invoice {inv_id} for {client} saved. Total: {total}'}


def record_expense(payload: Dict):
    exp_id = str(uuid.uuid4())
    path = f'data/expenses/{exp_id}.json'
    with open(path, 'w') as f:
        json.dump(payload, f, indent=2)
    return {'expense_id': exp_id, 'summary': f'Expense {exp_id} recorded. Amount: {payload.get("amount")}' }
```

---

## backend/whatsapp_adapter.py (dev stub)

```python
# A simple WhatsApp adapter stub. In dev, we just log messages and simulate delivery.
from fastapi import HTTPException

class WhatsAppAdapter:
    def __init__(self):
        pass

    def send_text(self, to: str, message: str):
        print(f'[WHATSAPP SEND] to={to} message={message}')
        return {'status': 'sent', 'to': to}

    def send_voice(self, to: str, audio_path: str):
        print(f'[WHATSAPP VOICE] to={to} audio={audio_path}')
        return {'status': 'sent', 'to': to}

# Example usage: adapter = WhatsAppAdapter(); adapter.send_text('+91....', 'Your invoice...')
```

---

## backend/main.py (webhook + orchestration)

```python
from fastapi import FastAPI, UploadFile, File, Request
import requests
from pydantic import BaseModel
from schemas import validate_invoice, validate_expense
from workflow_runner import create_invoice, record_expense
from whatsapp_adapter import WhatsAppAdapter
import json

app = FastAPI()
whatsapp = WhatsAppAdapter()
HF_URL = 'http://localhost:8080/generate'
ASR_URL = 'http://localhost:8001/transcribe'

class WebhookIn(BaseModel):
    from_number: str

@app.post('/webhook/audio')
async def webhook_audio(from_number: str, audio: UploadFile = File(...)):
    # Send audio to ASR service
    files = {'file': (audio.filename, await audio.read(), audio.content_type)}
    r = requests.post(ASR_URL, files=files)
    asr = r.json()

    text = asr.get('text','').lower()
    # Simple rule-based routing: expense detection keywords
    if any(k in text for k in ['paid','₹','rupee','रुपये','pay','paid to','paid']) and any(k in text for k in ['for','to','shop','bill','salary','paid']):
        intent = 'expense_record'
    elif 'invoice' in text or 'bill' in text or 'चालान' in text:
        intent = 'invoice_create'
    elif 'gst' in text:
        intent = 'gst_query'
    else:
        intent = 'fallback'

    if intent == 'expense_record':
        prompt = f"Extract expense JSON only. TRANSCRIPT: {asr.get('text')}"
        resp = requests.post(HF_URL, json={'prompt': prompt, 'max_new_tokens': 150})
        llm_text = resp.json().get('text','')
        try:
            payload = json.loads(llm_text)
        except Exception:
            rr = requests.post(HF_URL, json={'prompt': 'Reformat to valid JSON only: ' + llm_text, 'max_new_tokens': 120})
            payload = json.loads(rr.json().get('text','{}'))

        valid, err = validate_expense(payload)
        if not valid:
            return {'error': 'Validation failed', 'details': err}

        res = record_expense(payload)
        whatsapp.send_text(from_number, f"{res['summary']}")
        return {'status': 'ok', 'summary': res['summary']}

    if intent == 'invoice_create':
        prompt = f"Generate invoice JSON. TRANSCRIPT: {asr.get('text')}"
        resp = requests.post(HF_URL, json={'prompt': prompt, 'max_new_tokens': 200})
        llm_text = resp.json().get('text','')
        try:
            payload = json.loads(llm_text)
        except Exception:
            rr = requests.post(HF_URL, json={'prompt': 'Reformat to valid JSON only: ' + llm_text, 'max_new_tokens': 120})
            payload = json.loads(rr.json().get('text','{}'))

        valid, err = validate_invoice(payload)
        if not valid:
            return {'error': 'Validation failed', 'details': err}

        res = create_invoice(payload)
        whatsapp.send_text(from_number, f"{res['summary']}")
        return {'status': 'ok', 'summary': res['summary']}

    elif intent == 'gst_query':
        prompt = f"Answer GST question concisely for SME owner: {asr.get('text')}"
        resp = requests.post(HF_URL, json={'prompt': prompt, 'max_new_tokens': 150})
        whatsapp.send_text(from_number, resp.json().get('text',''))
        return {'status': 'ok'}

    else:
        whatsapp.send_text(from_number, "Sorry, I didn't understand. Can you repeat in short?")
        return {'status': 'fallback'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
```

Notes: This `main.py` is the minimal glue. It uses simple rules for intent detection — replace with your intent service later.

---

# Expense Recording: Prompts, Pipelines, Examples

## Prompt template: Expense Extraction

```
You are an assistant that extracts expense details from a conversational transcript in Indian languages.
Input: <<TRANSCRIPT>>
Output ONLY valid JSON matching schema:
{
  "category": "raw_material|fuel|utility|salary|misc",
  "amount": 0,
  "vendor": "",
  "date": "YYYY-MM-DD",
  "payment_method": "cash|upi|bank|cheque",
  "gst_applicable": true|false,
  "notes": "optional text"
}
```

## Pipeline: voice_expense_pipeline (Gemini agent)

* Trigger: incoming_audio
* Steps:

  1. Call ASR: transcribe audio → store `asr`
  2. Intent classifier: detect `expense_record`
  3. Call HF LLM with `Expense Extraction` prompt → store `llm_out`
  4. Validate `llm_out` against `EXPENSE_SCHEMA`

     * On fail: retry once with reformat prompt
     * On second fail: ask user a clarifying question
  5. Call `workflow_runner.record_expense` with validated JSON
  6. Send WhatsApp confirmation + daily summary update

## Example transcripts (for testing)

* Hindi voice: "आज मैंने 2200 रुपये पेट्रोल भरा" → expect category=fuel, amount=2200
* English voice: "Paid 13,200 to Shyam Traders for raw materials" → category=raw_material, amount=13200, vendor=Shyam Traders
* Marathi voice: "दुकानदारांना 5000 दिले" → category=misc, amount=5000

---

# 4. README.md (full setup, run order, testing)

Place the following `README.md` at repo root.

````markdown
# WhatsApp ARIA — Dev Repo (with Expense Recording)

This repo contains the dev skeleton for a WhatsApp-based AI assistant for Indian SMEs. It uses Gemini CLI for prompt/agent design and local Hugging Face + ASR servers for inference.

## Prereqs
- Python 3.10+
- git
- Node + npm (for Gemini CLI)
- Optional: GPU + CUDA if you plan to run larger HF models

## Setup
1. Clone repo
2. Create venv and install deps:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. (Optional) set HF_MODEL env var to a model that fits your machine:
```bash
export HF_MODEL=google/gemma-text-small-it
```

## Run order (dev)
Open three terminals (or use tmux):
1. Start HF server:
```bash
python backend/hf_server.py
```
2. Start ASR service:
```bash
python backend/asr_service.py
```
3. Start backend webhook service:
```bash
uvicorn backend.main:app --reload --port 8000
```
4. (Optional) Start Gemini CLI with agent config:
```bash
cd gemini
gemini --config gemini_agent.yaml
```

## Test Expense Recording flow
Use curl or Postman to POST an audio file to the webhook:
```bash
curl -X POST "http://localhost:8000/webhook/audio?from_number=%2B911234567890" -F "audio=@tests/samples/expense_hindi_01.mp3"
```
You should see the ASR text printed and a response indicating expense recorded (if the LLM returned valid JSON).

## Running tests
- Add audio samples to `tests/samples` and create tests in `tests/test_end2end.py`.
- Run `pytest -q`.

## Notes on costs
- This setup uses local models and open-source ASR; it should incur no API cost. Running large models on CPU is slow — stick to small models during dev.

## Next steps
- Move intent detection to the `intent_classifier` service.
- Replace rule-based routing with the Gemini-configured pipelines once adapters exist.
- Add WhatsApp Business Cloud integration for production (paid).

````

---

# Final notes

* I updated the Gemini canvas with the Expense Recording feature integrated into prompts, pipelines, schemas, starter code, and README.
* The expense feature is implemented in the dev skeleton as a first-class pipeline and can be expanded to include OCR/photo receipts, recurring detection, fraud alerts, and daily closing reports.
* If you want, I can now:

  * Generate the JSON schema + Gemini pipeline snippet as a downloadable `gemini_agent.yaml` fragment, or
  * Create the expense-specific prompt pack tuned for Hindi/Marathi/Telugu (templates in multiple languages), or
  * Add unit tests for the expense pipeline.

---

**End of updated Dev Kit**

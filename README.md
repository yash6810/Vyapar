# WhatsApp ARIA — Dev Repo (with Expense Recording)

This repo contains the dev skeleton for a WhatsApp-based AI assistant for Indian SMEs. It uses Gemini CLI for prompt/agent design and local Hugging Face + ASR servers for inference.

## Prereqs
- Python 3.10+
- git
- Node + npm (for Gemini CLI)
- `pip install -r requirements.txt` (which includes `python-dateutil`)
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

## Production Configuration (Optional)
To connect to the WhatsApp Business Cloud API, you will need to set the following environment variables:
- `WHATSAPP_API_KEY`: Your WhatsApp Cloud API token.
- `WHATSAPP_PHONE_NUMBER_ID`: The ID of the phone number you are sending from.

## Run order (dev)
Open four terminals (or use tmux):
1. Start HF server:
```bash
python backend/hf_server.py
```
2. Start ASR service:
```bash
python backend/asr_service.py
```
3. Start Intent Classifier service:
```bash
python backend/intent_classifier.py
```
4. Start backend webhook service:
```bash
uvicorn backend.main:app --reload --port 8000
```
5. (Optional) Start Gemini CLI with agent config:
```bash
cd gemini
gemini --config gemini_agent.yaml
```

## Test Expense Recording flow
Use curl or Postman to POST an audio file to the webhook. The ASR service now supports `.mp3`, `.wav`, `.ogg`, and `.flac` formats.
```bash
curl -X POST "http://localhost:8000/webhook/audio?from_number=%2B911234567890" -F "audio=@tests/samples/expense_hindi_01.mp3"
```
You should see the ASR text printed and a response indicating expense recorded (if the LLM returned valid JSON).

## Get Expenses
You can retrieve expenses for a specific date range by making a GET request to the `/expenses` endpoint. The `start_date` and `end_date` query parameters can be used to filter the expenses. The date format is `YYYY-MM-DD`.

Example:
```bash
curl -X GET "http://localhost:8000/expenses?start_date=2025-11-20&end_date=2025-11-21"
```

## Get Invoices
You can retrieve invoices for a specific date range by making a GET request to the `/invoices` endpoint. The `start_date` and `end_date` query parameters can be used to filter the invoices. The date format is `YYYY-MM-DD`.

Example:
```bash
curl -X GET "http://localhost:8000/invoices?start_date=2025-11-20&end_date=2025-11-21"
```

## Get Monthly Expense Summary
You can retrieve a monthly summary of expenses by making a GET request to the `/expenses/summary/monthly` endpoint. The `year` and `month` query parameters can be used to filter the expenses.

Example:
```bash
curl -X GET "http://localhost:8000/expenses/summary/monthly?year=2025&month=11"
```

## Get Monthly Invoice Summary
You can retrieve a monthly summary of invoices by making a GET request to the `/invoices/summary/monthly` endpoint. The `year` and `month` query parameters can be used to filter the invoices.

Example:
```bash
curl -X GET "http://localhost:8000/invoices/summary/monthly?year=2025&month=11"
```

## Get Yearly Expense Summary
You can retrieve a yearly summary of expenses by making a GET request to the `/expenses/summary/yearly` endpoint. The `year` query parameter can be used to filter the expenses.

Example:
```bash
curl -X GET "http://localhost:8000/expenses/summary/yearly?year=2025"
```

## Get Yearly Invoice Summary
You can retrieve a yearly summary of invoices by making a GET request to the `/invoices/summary/yearly` endpoint. The `year` query parameter can be used to filter the invoices.

Example:
```bash
curl -X GET "http://localhost:8000/invoices/summary/yearly?year=2025"
```

## Running tests
- Add audio samples to `tests/samples` and create tests in `tests/test_end2end.py`.
- Run `pytest -q`.

## Notes on costs
- This setup uses local models and open-source ASR; it should incur no API cost. Running large models on CPU is slow — stick to small models during dev.

## Next steps
- **Done:** Move intent detection to the `intent_classifier` service.
- **Done:** Replace rule-based routing with a call to a local language model. The `intent_classifier` service now uses the `hf_server` to classify intents.
- **Done:** Prepared the `whatsapp_adapter.py` for WhatsApp Business Cloud integration. To enable, set the `WHATSAPP_API_KEY` and `WHATSAPP_PHONE_NUMBER_ID` environment variables.
- **Done:** Added flexible date parsing for expenses. The application can now handle various date formats.
- **Done:** Added an endpoint to retrieve expenses for a specific date range.
- **Done:** Refactored the document processing logic to be more generic and extensible.
- **Done:** Added an endpoint to retrieve invoices for a specific date range.
- **Done:** Added an endpoint to retrieve a monthly summary of expenses.
- **Done:** Added an endpoint to retrieve a monthly summary of invoices.
- **Done:** Added an endpoint to retrieve a yearly summary of expenses.
- **Done:** Added an endpoint to retrieve a yearly summary of invoices.
- **Done:** Added tagging functionality for expenses and invoices.
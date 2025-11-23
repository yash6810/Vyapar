# VYAPAR - WhatsApp AI Assistant for Indian SMEs

This repository contains the development skeleton for a WhatsApp-based AI assistant designed for Indian Small and Medium-sized Enterprises (SMEs). It leverages the Gemini CLI for prompt and agent design, and local Hugging Face (HF) and Automatic Speech Recognition (ASR) servers for inference, enabling a powerful and cost-effective solution.

## Features

*   **WhatsApp Integration:** Designed to connect with the WhatsApp Business Cloud API for seamless communication.
*   **AI-Powered Assistant:** Utilizes local language models for intent classification and intelligent responses.
*   **Expense Recording:** Allows users to record expenses via audio messages, processed by the ASR service and classified by the LLM.
*   **Invoice Management:** Supports recording and retrieval of invoices.
*   **Flexible Date Parsing:** Handles various date formats for expense and invoice entries.
*   **Comprehensive Summaries:** Provides endpoints for retrieving daily, monthly, and yearly summaries of expenses and invoices.
*   **Tagging Functionality:** Enables tagging for expenses and invoices for better organization.
*   **Local Inference:** Uses local Hugging Face models and open-source ASR to minimize API costs.

## Prerequisites

Before you begin, ensure you have the following installed:

*   Python 3.10+
*   git
*   Node.js and npm (for Gemini CLI)
*   Optional: GPU + CUDA (if you plan to run larger Hugging Face models)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd Vyapar
    ```
2.  **Create a Python virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate # On Windows, use `.\.venv\Scripts\activate`
    pip install -r requirements.txt
    ```
    (The `requirements.txt` includes `python-dateutil` and other necessary packages.)
3.  **Optional: Set Hugging Face model environment variable:**
    You can specify a smaller model to fit your machine's resources.
    ```bash
    export HF_MODEL=google/gemma-text-small-it
    ```

## Production Configuration (Optional)

To connect to the WhatsApp Business Cloud API, you need to set the following environment variables:

*   `WHATSAPP_API_KEY`: Your WhatsApp Cloud API token.
*   `WHATSAPP_PHONE_NUMBER_ID`: The ID of the phone number you are sending from.

## Running in Development

Open four separate terminals (or use `tmux` for convenience) and run the following commands:

1.  **Start the Hugging Face server:**
    ```bash
    python backend/hf_server.py
    ```
2.  **Start the ASR service:**
    ```bash
    python backend/asr_service.py
    ```
3.  **Start the Intent Classifier service:**
    ```bash
    python backend/intent_classifier.py
    ```
4.  **Start the backend webhook service:**
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
5.  **Optional: Start Gemini CLI with agent configuration:**
    ```bash
    cd gemini
    gemini --config gemini_agent.yaml
    ```

## API Endpoints and Usage

The backend service exposes several endpoints for interacting with the system.

### Test Expense Recording Flow

You can test the expense recording by POSTing an audio file to the webhook. The ASR service supports `.mp3`, `.wav`, `.ogg`, and `.flac` formats.

```bash
curl -X POST "http://localhost:8000/webhook/audio?from_number=%2B911234567890" -F "audio=@tests/samples/expense_hindi_01.mp3"
```
You should see the ASR text printed and a response indicating the expense was recorded (if the LLM returned valid JSON).

### Retrieve Expenses

Retrieve expenses for a specific date range. The `start_date` and `end_date` query parameters use the `YYYY-MM-DD` format.

```bash
curl -X GET "http://localhost:8000/expenses?start_date=2025-11-20&end_date=2025-11-21"
```

### Retrieve Invoices

Retrieve invoices for a specific date range. The `start_date` and `end_date` query parameters use the `YYYY-MM-DD` format.

```bash
curl -X GET "http://localhost:8000/invoices?start_date=2025-11-20&end_date=2025-11-21"
```

### Retrieve Monthly Expense Summary

Retrieve a monthly summary of expenses. The `year` and `month` query parameters are used for filtering.

```bash
curl -X GET "http://localhost:8000/expenses/summary/monthly?year=2025&month=11"
```

### Retrieve Monthly Invoice Summary

Retrieve a monthly summary of invoices. The `year` and `month` query parameters are used for filtering.

```bash
curl -X GET "http://localhost:8000/invoices/summary/monthly?year=2025&month=11"
```

### Retrieve Yearly Expense Summary

Retrieve a yearly summary of expenses. The `year` query parameter is used for filtering.

```bash
curl -X GET "http://localhost:8000/expenses/summary/yearly?year=2025"
```

### Retrieve Yearly Invoice Summary

Retrieve a yearly summary of invoices. The `year` query parameter is used for filtering.

```bash
curl -X GET "http://localhost:8000/invoices/summary/yearly?year=2025"
```

## Running Tests

1.  Add audio samples to `tests/samples/`.
2.  Create corresponding tests in `tests/test_end2end.py`.
3.  Run `pytest`:
    ```bash
    pytest -q
    ```

## Notes on Costs

This setup utilizes local models and open-source ASR, which should incur no API costs. Running large models on a CPU can be slow; it is recommended to stick to smaller models during development.

# Architecture

This document describes the overall architecture of the WhatsApp ARIA system for voice-based expense recording for SMEs.

## High-Level Overview

The system is designed as a microservices-oriented architecture, primarily built with FastAPI for the backend services. It leverages an Automatic Speech Recognition (ASR) service to convert WhatsApp voice messages into text, a Large Language Model (LLM) server for extracting structured information (like expense details) from the transcribed text, and a workflow runner to process and store this information. A WhatsApp adapter handles communication with users.

```mermaid
graph TD
    User[User via WhatsApp] --> |Voice Message| WhatsAppWebhook[WhatsApp Webhook (backend/main.py)]
    WhatsAppWebhook --> |Audio File| ASRService[ASR Service (backend/asr_service.py)]
    ASRService --> |Transcribed Text| WhatsAppWebhook
    WhatsAppWebhook --> |Text + Prompt| LLMServer[LLM Server (backend/hf_server.py)]
    LLMServer --> |Extracted JSON| WhatsAppWebhook
    WhatsAppWebhook --> |Validated JSON| WorkflowRunner[Workflow Runner (backend/workflow_runner.py)]
    WorkflowRunner --> |Store Data| DataStorage[(Data Storage)]
    DataStorage --> |Expenses/Invoices| ExpenseRecords[Expense Records]
    WhatsAppWebhook --> |Confirmation/Summary| WhatsAppAdapter[WhatsApp Adapter (backend/whatsapp_adapter.py)]
    WhatsAppAdapter --> |Text Message| User
```

## Components

### 1. WhatsApp Webhook (`backend/main.py`)

*   **Functionality:**
    *   Receives incoming audio messages from WhatsApp (simulated or actual webhook).
    *   Acts as the orchestrator, routing requests to appropriate microservices.
    *   Performs intent detection (currently rule-based).
    *   Sends responses back to the user via the WhatsApp Adapter.
*   **Technologies:** FastAPI, requests library for inter-service communication.

### 2. ASR Service (`backend/asr_service.py`)

*   **Functionality:** Transcribes audio files (voice messages) into text.
*   **Technologies:** FastAPI, Whisper (or other ASR models like Indic ASR).
*   **Deployment:** Can be deployed as a separate microservice.

### 3. LLM Server (`backend/hf_server.py`)

*   **Functionality:**
    *   Hosts a local Large Language Model (e.g., Hugging Face models like Gemma).
    *   Generates structured JSON output (e.g., expense details) based on text prompts and transcribed audio.
*   **Technologies:** FastAPI, Hugging Face Transformers library.
*   **Deployment:** Can be deployed as a separate microservice. Model choice dependent on available resources (CPU/GPU).

### 4. Workflow Runner (`backend/workflow_runner.py`)

*   **Functionality:**
    *   Contains the core business logic for processing validated data.
    *   Currently supports `record_expense` and `create_invoice` functions.
    *   Stores processed data (JSON files) into a local file system (`data/expenses`, `data/invoices`).
*   **Technologies:** Python, JSON for data storage.

### 5. Schemas (`backend/schemas.py`)

*   **Functionality:** Defines JSON schemas for various data structures (e.g., `EXPENSE_SCHEMA`, `INVOICE_SCHEMA`).
    *   Provides validation functions to ensure data integrity before processing.
*   **Technologies:** Python, `jsonschema` library.

### 6. WhatsApp Adapter (`backend/whatsapp_adapter.py`)

*   **Functionality:** A stub implementation for sending text and voice messages back to WhatsApp users.
*   **Deployment:** In MVP, this is a print-to-console stub. For production, this would integrate with WhatsApp Business Cloud API.

### 7. Data Storage (`backend/data/`)

*   **Functionality:** Simple file-based storage for recorded expenses and invoices.
*   **Deployment:** For MVP, local JSON files. Can be replaced with a database (SQL/NoSQL) in later stages.

## Data Flow for Expense Recording

1.  **User sends voice message:** A user records and sends a voice message via WhatsApp (e.g., "आज मैंने 2200 रुपये पेट्रोल भरा").
2.  **Webhook receives audio:** The `main.py` webhook endpoint receives the audio file and the sender's number.
3.  **ASR Transcription:** The audio is sent to the `asr_service.py` which transcribes it into text (e.g., "आज मैंने 2200 रुपये पेट्रोल भरा").
4.  **Intent Detection:** `main.py` uses simple rule-based matching to determine the user's intent (e.g., `expense_record`).
5.  **LLM Extraction:** The transcribed text is sent to the `hf_server.py` along with a prompt to extract structured expense JSON. The LLM returns a JSON object (e.g., `{"category": "fuel", "amount": 2200, "date": "YYYY-MM-DD", ...}`).
6.  **JSON Validation:** The extracted JSON is validated against `EXPENSE_SCHEMA` using `schemas.py`.
7.  **Expense Recording:** If valid, the JSON payload is passed to `workflow_runner.py`'s `record_expense` function, which saves it as a JSON file in `data/expenses/`.
8.  **Confirmation to User:** A confirmation message (e.g., "Expense recorded: Amount: 2200") is sent back to the user via the `whatsapp_adapter.py`.

## Future Enhancements (Beyond MVP)

*   **Robust Intent Detection:** Replace rule-based intent detection with a dedicated machine learning model or Gemini's more advanced intent services.
*   **Database Integration:** Migrate from file-based storage to a proper database for scalability and query capabilities.
*   **Full WhatsApp Cloud API Integration:** Implement full integration for richer messaging, media handling, and message status updates.
*   **Advanced Features:** Integrate deferred scope items like GST workflows, OCR bill scanning, fraud detection.
*   **Error Handling and Logging:** Enhance error handling, add comprehensive logging, and monitoring.
# Task Summary

This document provides a summary of the features implemented in the application and instructions on how to run it.

## Completed Tasks

- [x] **Modular Architecture:** The application has been refactored into a modular architecture with separate services for different functionalities like ASR, intent classification, and the main backend.
- [x] **AI-based Intent Detection:** The intent detection has been upgraded from a rule-based system to an AI-based system that uses a language model for more accurate and flexible intent classification.
- [x] **Production-Ready WhatsApp Integration:** The WhatsApp adapter has been prepared for production use with clear instructions on how to configure it with API credentials.
- [x] **Comprehensive Test Suite:** The application now has a comprehensive test suite with unit tests and end-to-end tests for all the major features.
- [x] **Robust Error Handling:** The application now has robust error handling to gracefully handle service outages and other unexpected errors.
- [x] **Detailed Logging:** The application now has detailed logging with request ID tracing, which makes it easier to debug and monitor the application.
- [x] **Health Check Endpoint:** A `/health` endpoint has been added to monitor the status of the application and its dependent services.
- [x] **Expense and Invoice Summaries:** The application now provides daily, monthly, and yearly summaries for both expenses and invoices.
- [x] **Flexible Date Parsing:** The application can now handle various date formats for expenses and invoices.
- [x] **Multi-currency Support:** The application now supports multiple currencies for expenses and invoices.
- [x] **Generic Document Processing:** The document processing logic has been refactored to be more generic and extensible, which will make it easier to add support for other document types in the future.
- [x] **Expanded Audio Format Support:** The ASR service now supports a wider range of audio formats, including `.ogg` and `.flac`.
- [x] **Search by Vendor:** Added the ability to search for expenses and invoices by vendor.
- [x] **Tagging:** Added tagging functionality for expenses and invoices.

## How to Run

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Services:**
    Open four terminals and run the following commands in each terminal:

    -   **HF Server:**
        ```bash
        python backend/hf_server.py
        ```

    -   **ASR Service:**
        ```bash
        python backend/asr_service.py
        ```

    -   **Intent Classifier Service:**
        ```bash
        python backend/intent_classifier.py
        ```

    -   **Backend Service:**
        ```bash
        uvicorn backend.main:app --reload --port 8000
        ```

## API Endpoints

-   **POST /webhook/audio:**
    -   **Description:** This is the main endpoint for processing audio messages. It takes an audio file and a `from_number` as input, transcribes the audio, detects the intent, and then processes the request based on the intent.
    -   **Example:**
        ```bash
        curl -X POST "http://localhost:8000/webhook/audio?from_number=%2B911234567890" -F "audio=@tests/samples/expense_hindi_01.mp3"
        ```

-   **GET /health:**
    -   **Description:** This endpoint returns the status of the application and its dependent services.
    -   **Example:**
        ```bash
        curl -X GET "http://localhost:8000/health"
        ```

-   **GET /expenses:**
    -   **Description:** This endpoint returns a list of expenses for a specific date range, optionally filtered by vendor.
    -   **Example:**
        ```bash
        curl -X GET "http://localhost:8000/expenses?start_date=2025-11-20&end_date=2025-11-21&vendor=YourVendorName"
        ```

-   **GET /invoices:**
    -   **Description:** This endpoint returns a list of invoices for a specific date range, optionally filtered by vendor.
    -   **Example:**
        ```bash
        curl -X GET "http://localhost:8000/invoices?start_date=2025-11-20&end_date=2025-11-21&vendor=YourVendorName"
        ```

-   **GET /expenses/summary/daily:**
    -   **Description:** This endpoint returns a daily summary of expenses, grouped by currency.
    -   **Example:**
        ```bash
        curl -X GET "http://localhost:8000/expenses/summary/daily"
        ```

-   **GET /expenses/summary/monthly:**
    -   **Description:** This endpoint returns a monthly summary of expenses, grouped by currency.
    -   **Example:**
        ```bash
        curl -X GET "http://localhost:8000/expenses/summary/monthly?year=2025&month=11"
        ```

-   **GET /expenses/summary/yearly:**
    -   **Description:** This endpoint returns a yearly summary of expenses, grouped by currency.
    -   **Example:**
        ```bash
        curl -X GET "http://localhost:8000/expenses/summary/yearly?year=2025"
        ```

-   **GET /invoices/summary/monthly:**
    -   **Description:** This endpoint returns a monthly summary of invoices, grouped by currency.
    -   **Example:**
        ```bash
        curl -X GET "http://localhost:8000/invoices/summary/monthly?year=2025&month=11"
        ```

-   **GET /invoices/summary/yearly:**
    -   **Description:** This endpoint returns a yearly summary of invoices, grouped by currency.
    -   **Example:**
        ```bash
        curl -X GET "http://localhost:8000/invoices/summary/yearly?year=2025"
        ```
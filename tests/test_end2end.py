import pytest
import requests
import os
import time

# --- Configuration ---
BACKEND_URL = "http://localhost:8000"
ASR_URL = "http://localhost:8001"
HF_URL = "http://localhost:8080"

# Sample audio paths (these should exist in tests/samples)
SAMPLE_AUDIO_HINDI = "tests/samples/expense_hindi_01.mp3" # Placeholder - actual file needs to be added by user
SAMPLE_AUDIO_ENGLISH = "tests/samples/expense_english_01.mp3" # Placeholder

@pytest.fixture(scope="module", autouse=True)
def ensure_services_are_running():
    """
    Ensures that backend, ASR, and HF services are running before tests start.
    This fixture will attempt to connect to the services.
    """
    print("\nAttempting to connect to services...")
    services = {
        "Backend": BACKEND_URL,
        "ASR": ASR_URL,
        "HF Server": HF_URL
    }
    for service_name, url in services.items():
        max_retries = 10
        for i in range(max_retries):
            try:
                # For FastAPI, a simple GET on the base URL usually works
                # Or a specific health check endpoint if available
                response = requests.get(url + "/docs", timeout=1) 
                if response.status_code == 200:
                    print(f"{service_name} is running.")
                    break
            except requests.exceptions.ConnectionError:
                print(f"Waiting for {service_name} to start at {url}...")
                time.sleep(2)
        else:
            pytest.fail(f"{service_name} did not start within the expected time.")
    yield
    print("\nServices check complete.")

@pytest.mark.skip(reason="Requires actual audio samples and running services")
def test_end_to_end_expense_recording_hindi():
    """
    Tests the end-to-end flow for Hindi voice expense recording.
    """
    if not os.path.exists(SAMPLE_AUDIO_HINDI):
        pytest.skip(f"Sample audio file not found: {SAMPLE_AUDIO_HINDI}")

    with open(SAMPLE_AUDIO_HINDI, "rb") as f:
        files = {'audio': (os.path.basename(SAMPLE_AUDIO_HINDI), f, 'audio/mpeg')}
        headers = {'accept': 'application/json'}
        params = {'from_number': '+919876543210'}

        response = requests.post(
            f"{BACKEND_URL}/webhook/audio",
            params=params,
            files=files,
            headers=headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
...
    assert 'summary' in data
    assert 'Expense recorded' in data['summary']

@pytest.mark.skip(reason="Requires running services")
def test_health_check():
    """
    Tests the /health endpoint.
    """
    response = requests.get(f"{BACKEND_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert "asr_service" in data
    assert "intent_classifier" in data
    assert "hf_server" in data

@pytest.mark.skip(reason="Requires running services")
def test_daily_expense_summary():
    """
    Tests the /expenses/summary/daily endpoint.
    """
    response = requests.get(f"{BACKEND_URL}/expenses/summary/daily")
    assert response.status_code == 200
    data = response.json()
    assert "total_amount" in data
    assert "expense_count" in data
    assert data["total_amount"] == 1000
    assert data["expense_count"] == 1
    # Cleanup dummy files
    os.remove("data/expenses/test_expense_today.json")
    os.remove("data/expenses/test_expense_yesterday.json")

@pytest.mark.skip(reason="Requires actual audio samples and running services")
def test_end_to_end_expense_recording_english():
    """
    Tests the end-to-end flow for English voice expense recording.
    """
    if not os.path.exists(SAMPLE_AUDIO_ENGLISH):
        pytest.skip(f"Sample audio file not found: {SAMPLE_AUDIO_ENGLISH}")

    with open(SAMPLE_AUDIO_ENGLISH, "rb") as f:
        files = {'audio': (os.path.basename(SAMPLE_AUDIO_ENGLISH), f, 'audio/mpeg')}
        headers = {'accept': 'application/json'}
        params = {'from_number': '+919988776655'}

        response = requests.post(
            f"{BACKEND_URL}/webhook/audio",
            params=params,
            files=files,
            headers=headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert 'summary' in data
    assert 'Expense recorded' in data['summary']

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.intent_classifier import app

client = TestClient(app)

@pytest.mark.parametrize("text, expected_intent", [
    ("paid 1000 for raw materials", "expense_record"),
    ("send an invoice to John Doe", "invoice_create"),
    ("what is the gst rate for electronics", "gst_query"),
    ("hello how are you", "fallback"),
])
@patch('backend.intent_classifier.requests.post')
def test_classify_intent(mock_post, text, expected_intent):
    # Mock the response from the hf_server
    mock_post.return_value.json.return_value = {'text': f'Intent: {expected_intent}'}

    response = client.post("/classify", json={"text": text})
    assert response.status_code == 200
    assert response.json() == {"intent": expected_intent}

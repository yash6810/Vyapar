# Intent classifier microservice
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()
HF_URL = 'http://localhost:8080/generate'

class ClassifyRequest(BaseModel):
    text: str

@app.post('/classify')
async def classify(req: ClassifyRequest):
    text = req.text.lower()
    prompt = f"""You are an intent classifier. Classify the following text into one of these categories: expense_record, invoice_create, gst_query, fallback.
    Text: "{text}"
    Intent:"""
    
    resp = requests.post(HF_URL, json={'prompt': prompt, 'max_new_tokens': 10})
    llm_text = resp.json().get('text','')
    
    # The model might return the prompt plus the intent, so we extract the last line
    intent = llm_text.splitlines()[-1].replace('Intent:','').strip()

    # Basic validation to ensure the intent is one of the allowed values
    if intent not in ['expense_record', 'invoice_create', 'gst_query', 'fallback']:
        intent = 'fallback'

    return {'intent': intent}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('intent_classifier:app', host='0.0.0.0', port=8002)


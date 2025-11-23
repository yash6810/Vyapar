# Intent classifier microservice
from fastapi import FastAPI
from pydantic import BaseModel
import logging

app = FastAPI()

class ClassifyRequest(BaseModel):
    text: str

@app.post('/classify')
async def classify(req: ClassifyRequest):
    text = req.text.lower()
    
    # Keyword-based intent classification for reliability
    if any(keyword in text for keyword in ["gst", "tax", "hsn", "invoice fields", "input tax credit"]):
        intent = 'gst_query'
    elif any(keyword in text for keyword in ["invoice for", "bill to"]):
        intent = 'invoice_create'
    elif any(keyword in text for keyword in ["spent", "paid", "expense of", "bought"]):
        intent = 'expense_record'
    else:
        intent = 'fallback'

    logging.info(f"Classified '{text}' as '{intent}'")
    return {'intent': intent}

if __name__ == '__main__':
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run('intent_classifier:app', host='0.0.0.0', port=8002)

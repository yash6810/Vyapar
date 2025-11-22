import sys
import os
from sqlalchemy.orm import Session
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import Depends, FastAPI, UploadFile, File, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import requests
from pydantic import BaseModel
from . import crud, models, schemas, auth
from .database import SessionLocal, engine
from .workflow_runner import create_invoice, record_expense
from .config import settings
from jose import JWTError, jwt
from whatsapp_adapter import WhatsAppAdapter
import json
import logging
import uuid
from typing import Optional
from datetime import datetime, date, timedelta
import easyocr
import io

models.Base.metadata.create_all(bind=engine)

# Configure logging
formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(request_id)s] - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
file_handler = logging.FileHandler("backend.log")
file_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(file_handler)

# Initialize the OCR reader once
try:
    ocr_reader = easyocr.Reader(['en', 'hi'])
    logging.info("EasyOCR reader initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize EasyOCR reader: {e}")
    ocr_reader = None

whatsapp = WhatsAppAdapter()

class WebhookIn(BaseModel):
    from_number: str

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    
    # Add request_id to log record
    extra = {'request_id': request_id}
    old_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.request_id = extra['request_id']
        return record
    logging.setLogRecordFactory(record_factory)

    response = await call_next(request)
    return response

import easyocr
import io
from PIL import Image

# Initialize the OCR reader once
# This can take a moment the first time it runs
try:
    ocr_reader = easyocr.Reader(['en', 'hi'])
    logging.info("EasyOCR reader initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize EasyOCR reader: {e}")
    ocr_reader = None

async def process_document(intent: str, asr_text: str, from_number: str, db: Session, current_user: schemas.User):
    if intent == 'expense_record':
        doc_type = 'expense'
        runner = record_expense
        prompt = f"Extract expense JSON only from the following text. The JSON should contain 'date', 'item', and 'amount'. TEXT: {asr_text}"
        max_tokens = 150
    elif intent == 'invoice_create':
        doc_type = 'invoice'
        runner = create_invoice
        prompt = f"Generate invoice JSON from the following text. The JSON should contain 'date', 'customer_name', and 'amount'. TEXT: {asr_text}"
        max_tokens = 200
    else:
        return

    try:
        resp = requests.post(settings.HF_URL, json={'prompt': prompt, 'max_new_tokens': max_tokens})
        resp.raise_for_status()
        llm_text = resp.json().get('text','')
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"HF server unavailable: {e}")
    try:
        payload = json.loads(llm_text)
    except Exception:
        try:
            rr = requests.post(settings.HF_URL, json={'prompt': 'Reformat to valid JSON only: ' + llm_text, 'max_new_tokens': 120})
            rr.raise_for_status()
            payload = json.loads(rr.json().get('text','{}'))
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"HF server unavailable: {e}")

    if doc_type == 'expense':
        # Assuming the LLM returns date, item, amount
        expense = schemas.ExpenseCreate(date=payload.get('date'), item=payload.get('item'), amount=payload.get('amount'))
        res = runner(db, expense, current_user.id)
        summary = f"Expense recorded: {res.item} for {res.amount}"
    else:
        # Assuming the LLM returns date, customer_name, amount
        invoice = schemas.InvoiceCreate(date=payload.get('date'), customer_name=payload.get('customer_name'), amount=payload.get('amount'))
        res = runner(db, invoice, current_user.id)
        summary = f"Invoice created for {res.customer_name} for {res.amount}"


    whatsapp.send_text(from_number, summary)
    logging.info(f"{doc_type.capitalize()} recorded for {from_number}")
    return {'status': 'ok', 'summary': summary}

@app.post('/webhook/image')
async def webhook_image(image: UploadFile = File(...), current_user: schemas.User = Depends(get_current_user)):
    logging.info(f"Received image from {current_user.email}")

    if not ocr_reader:
        raise HTTPException(status_code=503, detail="OCR service is not available.")

    try:
        image_bytes = await image.read()
        
        # Use EasyOCR to read text
        # The detail=0 argument returns a list of strings
        ocr_results = ocr_reader.readtext(image_bytes, detail=0, paragraph=True)
        ocr_text = " ".join(ocr_results)
        
        logging.info(f"OCR Extracted Text: {ocr_text}")

        # Now, use the LLM to extract structured data from the OCR text
        prompt = f"From the following OCR text from a receipt, extract a JSON object with keys 'Total Amount', 'Vendor', and 'Date'. OCR TEXT: {ocr_text}"
        
        resp = requests.post(settings.HF_URL, json={'prompt': prompt, 'max_new_tokens': 150})
        resp.raise_for_status()
        llm_text = resp.json().get('text', '{}')
        
        # Basic parsing of the LLM output
        extracted_data = json.loads(llm_text)
        
        return extracted_data

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process image: {e}")


@app.post('/webhook/audio')
async def webhook_audio(from_number: str, audio: UploadFile = File(...), db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    logging.info(f"Received audio from {from_number}")
    # Send audio to ASR service
    files = {'file': (audio.filename, await audio.read(), audio.content_type)}
    try:
        r = requests.post(settings.ASR_URL, files=files)
        r.raise_for_status()
        asr = r.json()
        logging.info(f"ASR response: {asr}")
    except requests.exceptions.RequestException as e:
        logging.error(f"ASR service unavailable: {e}")
        raise HTTPException(status_code=503, detail=f"ASR service unavailable: {e}")

    text = asr.get('text','').lower()
    
    # Call intent classifier service
    try:
        r = requests.post(settings.INTENT_URL, json={'text': text})
        r.raise_for_status()
        intent = r.json().get('intent')
        logging.info(f"Intent: {intent}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Intent classifier service unavailable: {e}")
        raise HTTPException(status_code=503, detail=f"Intent classifier service unavailable: {e}")

    if intent in ['expense_record', 'invoice_create']:
        return await process_document(intent, asr.get('text'), from_number, db, current_user)
    elif intent == 'gst_query':
        prompt = f"Answer GST question concisely for SME owner: {asr.get('text')}"
        try:
            resp = requests.post(settings.HF_URL, json={'prompt': prompt, 'max_new_tokens': 150})
            resp.raise_for_status()
            whatsapp.send_text(from_number, resp.json().get('text',''))
        except requests.exceptions.RequestException as e:
            logging.error(f"HF server unavailable: {e}")
            raise HTTPException(status_code=503, detail=f"HF server unavailable: {e}")
        return {'status': 'ok'}

    else:
        whatsapp.send_text(from_number, "Sorry, I didn't understand. Can you repeat in short?")
        logging.info(f"Fallback for {from_number}")
        return {'status': 'fallback'}

class TextMessage(BaseModel):
    text: str

@app.post('/webhook/text')
async def webhook_text(message: TextMessage, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    logging.info(f"Received text from {current_user.email}: {message.text}")
    
    text = message.text.lower()
    
    # Call intent classifier service
    try:
        r = requests.post(settings.INTENT_URL, json={'text': text})
        r.raise_for_status()
        intent = r.json().get('intent')
        logging.info(f"Intent: {intent}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Intent classifier service unavailable: {e}")
        raise HTTPException(status_code=503, detail=f"Intent classifier service unavailable: {e}")

    if intent in ['expense_record', 'invoice_create']:
        return await process_document(intent, message.text, current_user.email, db, current_user)
    elif intent == 'gst_query':
        prompt = f"Answer GST question concisely for SME owner: {message.text}"
        try:
            resp = requests.post(settings.HF_URL, json={'prompt': prompt, 'max_new_tokens': 150})
            resp.raise_for_status()
            return {"text": resp.json().get('text','')}
        except requests.exceptions.RequestException as e:
            logging.error(f"HF server unavailable: {e}")
            raise HTTPException(status_code=503, detail=f"HF server unavailable: {e}")
    else:
        return {"text": "Sorry, I didn't understand. Can you repeat in short?"}


@app.get('/health')
async def health_check():
    services = {
        "asr_service": settings.ASR_URL,
        "intent_classifier": settings.INTENT_URL,
        "hf_server": settings.HF_URL.replace('/generate', '')
    }
    service_status = {}
    for service_name, url in services.items():
        try:
            r = requests.get(url + "/docs", timeout=1)
            if r.status_code == 200:
                service_status[service_name] = "ok"
            else:
                service_status[service_name] = "error"
        except requests.exceptions.RequestException:
            service_status[service_name] = "unavailable"
        return service_status
    
    
    @app.post('/webhook/image')
    async def webhook_image(image: UploadFile = File(...), current_user: schemas.User = Depends(get_current_user)):
        logging.info(f"Received image from {current_user.email}")
    
        if not ocr_reader:
            raise HTTPException(status_code=503, detail="OCR service is not available.")
    
        try:
            image_bytes = await image.read()
            
            # Use EasyOCR to read text
            ocr_results = ocr_reader.readtext(image_bytes, detail=0, paragraph=True)
            ocr_text = " ".join(ocr_results)
            
            logging.info(f"OCR Extracted Text: {ocr_text}")
    
            # Now, use the LLM to extract structured data from the OCR text
            prompt = f"From the following OCR text from a receipt, extract a JSON object with keys 'Total Amount', 'Vendor', and 'Date'. OCR TEXT: {ocr_text}"
            
            resp = requests.post(settings.HF_URL, json={'prompt': prompt, 'max_new_tokens': 150})
            resp.raise_for_status()
            llm_text = resp.json().get('text', '{}')
            
            # Basic parsing of the LLM output to find the JSON
            try:
                json_start = llm_text.index('{')
                json_end = llm_text.rindex('}') + 1
                json_str = llm_text[json_start:json_end]
                extracted_data = json.loads(json_str)
            except (ValueError, json.JSONDecodeError):
                logging.error(f"Could not parse JSON from LLM response: {llm_text}")
                # Attempt to reformat if parsing fails
                reformat_prompt = f"Reformat the following text into a valid JSON object only: {llm_text}"
                rr = requests.post(settings.HF_URL, json={'prompt': reformat_prompt, 'max_new_tokens': 120})
                rr.raise_for_status()
                reformatted_text = rr.json().get('text', '{}')
                extracted_data = json.loads(reformatted_text)
    
            return extracted_data
    
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process image: {e}")
    
    
    # Users
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User], dependencies=[Depends(get_current_user)])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(get_current_user)])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# Expenses
@app.post("/users/{user_id}/expenses/", response_model=schemas.Expense, dependencies=[Depends(get_current_user)])
def create_expense_for_user(
    user_id: int, expense: schemas.ExpenseCreate, db: Session = Depends(get_db)
):
    return crud.create_expense(db=db, expense=expense, user_id=user_id)


@app.get("/expenses/", response_model=list[schemas.Expense], dependencies=[Depends(get_current_user)])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    expenses = crud.get_expenses(db, skip=skip, limit=limit)
    return expenses


@app.get("/expenses/{expense_id}", response_model=schemas.Expense, dependencies=[Depends(get_current_user)])
def read_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = crud.get_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense


@app.put("/expenses/{expense_id}", response_model=schemas.Expense, dependencies=[Depends(get_current_user)])
def update_expense(
    expense_id: int, expense: schemas.ExpenseCreate, db: Session = Depends(get_db)
):
    db_expense = crud.update_expense(db, expense_id=expense_id, expense=expense)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense


@app.delete("/expenses/{expense_id}", response_model=schemas.Expense, dependencies=[Depends(get_current_user)])
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = crud.delete_expense(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_expense


# Invoices
@app.post("/users/{user_id}/invoices/", response_model=schemas.Invoice, dependencies=[Depends(get_current_user)])
def create_invoice_for_user(
    user_id: int, invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)
):
    return crud.create_invoice(db=db, invoice=invoice, user_id=user_id)


@app.get("/invoices/", response_model=list[schemas.Invoice], dependencies=[Depends(get_current_user)])
def read_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    invoices = crud.get_invoices(db, skip=skip, limit=limit)
    return invoices


@app.get("/invoices/{invoice_id}", response_model=schemas.Invoice, dependencies=[Depends(get_current_user)])
def read_invoice(invoice_id: int, db: Session = Depends(get_db)):
    db_invoice = crud.get_invoice(db, invoice_id=invoice_.id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice


@app.put("/invoices/{invoice_id}", response_model=schemas.Invoice, dependencies=[Depends(get_current_user)])
def update_invoice(
    invoice_id: int, invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)
):
    db_invoice = crud.update_invoice(db, invoice_id=invoice_id, invoice=invoice)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice


@app.delete("/invoices/{invoice_id}", response_model=schemas.Invoice, dependencies=[Depends(get_current_user)])
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    db_invoice = crud.delete_invoice(db, invoice_id=invoice_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
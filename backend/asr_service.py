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

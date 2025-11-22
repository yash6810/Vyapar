# ASR microservice - transcribes an uploaded audio file.
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import tempfile
import torch
import whisperx
import gc 

app = FastAPI()

device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 16 
compute_type = "float16" if torch.cuda.is_available() else "int8"

# 1. Transcribe with original whisper (batched)
model = whisperx.load_model("small", device, compute_type=compute_type)

...
@app.post('/transcribe')
async def transcribe(file: UploadFile = File(...)):
    if file.filename.endswith('.mp3'):
        suffix = '.mp3'
    elif file.filename.endswith('.wav'):
        suffix = '.wav'
    elif file.filename.endswith('.ogg'):
        suffix = '.ogg'
    elif file.filename.endswith('.flac'):
        suffix = '.flac'
    else:
        suffix = '.tmp'
    
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
...
        tmp.write(await file.read())
        tmp.flush()
        res = model.transcribe(tmp.name)
    return {'text': res['text'], 'language_code': res.get('language', 'unknown'), 'confidence': 0.9}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('asr_service:app', host='0.0.0.0', port=8001)

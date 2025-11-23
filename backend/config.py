from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    HF_MODEL: str = "distilgpt2"
    HF_URL: str = "http://hf:8080/generate"
    ASR_URL: str = "http://asr:8001/transcribe"
    INTENT_URL: str = "http://intent:8002/classify"
    RAG_URL: str = "http://rag:8003/retrieve"

    MYSQL_HOST: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str


    class Config:
        env_file = ".env"

settings = Settings()

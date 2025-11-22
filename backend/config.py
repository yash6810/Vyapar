from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    HF_MODEL: str = "distilgpt2"
    HF_URL: str = "http://localhost:8080/generate"
    ASR_URL: str = "http://localhost:8001/transcribe"
    INTENT_URL: str = "http://localhost:8002/classify"

    class Config:
        env_file = ".env"

settings = Settings()

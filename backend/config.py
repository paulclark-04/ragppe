import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "MultiSummarizer"
    PROJECT_VERSION: str = "0.1.0"
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_credentials.json")
    
    # LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral:7b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Storage
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploads")

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

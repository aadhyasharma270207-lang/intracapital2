import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "INTRACAPITAL Backend"
    PROJECT_ENV: str = os.getenv("PROJECT_ENV", "development")
    
    # Model Configurations
    GRANITE_MODEL: str = os.getenv("GRANITE_MODEL", "granite3-dense:8b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Vector Database
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    # Knowledge Graph
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # Application Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./intracapital.db")
    
    # Frontend URL (CORS)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # General Options
    ENABLE_EXTERNAL_DATA: bool = os.getenv("ENABLE_EXTERNAL_DATA", "false").lower() == "true"
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
    
    # Upload folder
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

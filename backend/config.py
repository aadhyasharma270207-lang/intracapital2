import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "sample_company"
UPLOADS_DIR = BASE_DIR / "uploads"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

# Ensure runtime directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

# IBM Watsonx.ai Credentials
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_MODEL_ID = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-instruct-v2")

# Internal API Authentication token (Streamlit -> FastAPI)
FASTAPI_INTERNAL_API_KEY = os.getenv("FASTAPI_INTERNAL_API_KEY", "")

# Server configuration
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# Demo Mode status
DEMO_MODE = not (bool(WATSONX_API_KEY) and bool(WATSONX_PROJECT_ID))

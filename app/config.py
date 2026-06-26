# config.py: Configuration settings for the application
import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the root directory and load the environment variables from the .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings:
    """
    Settings class to hold all project configurations.
    Uses environment variables with safe defaults.
    """
    PROJECT_NAME: str = "TaskSphere API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security Configurations
    # In production, this MUST be a strong, randomly generated secret key
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-that-no-one-can-guess-1234567890")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./practice.db")
    
    # Upload Configurations
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

# Instantiate settings
settings = Settings()

# Ensure the upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

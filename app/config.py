import os
from dotenv import load_dotenv

# 1. Locate and load the .env file from the root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

class Config:
    """
    Reads configuration values strictly from environment variables populated by dotenv.
    If a variable is missing, it will raise an error or return a safe default indicator.
    """
    # Core Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "RetailIQ")
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # Security & Authentication (Crucial secrets have no code fallback)
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Third-Party AI / LLM Configurations
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
    
    # File Upload Configurations
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "storage/uploads")
    DETECTED_DIR: str = os.getenv("DETECTED_DIR", "storage/detected_images")

    @classmethod
    def validate_required_secrets(cls):
        """Ensures the app won't boot up if critical credentials are completely missing from .env"""
        critical_vars = ["SECRET_KEY", "DATABASE_URL", "GROQ_API_KEY"]
        missing = [var for var in critical_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"CRITICAL ERROR: Missing required environment variables in .env: {', '.join(missing)}")

# Validate secrets as soon as config is loaded by the app
Config.validate_required_secrets()
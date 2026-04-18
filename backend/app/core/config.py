import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "AI Job Readiness Analyzer"
    DEBUG: bool = False
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "your-access-key-id")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "your-secret-access-key")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "job-readiness-uploads")

    APPLY_THRESHOLD: int = int(os.getenv("APPLY_THRESHOLD", "80"))
    IMPROVE_THRESHOLD: int = int(os.getenv("IMPROVE_THRESHOLD", "50"))

    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "job_readiness")

settings = Settings()
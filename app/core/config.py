import os
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings and configuration"""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-12345678")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/mindwhile_books")
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MindWhile ERP - Book Sales"
    
settings = Settings()

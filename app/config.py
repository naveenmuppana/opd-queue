from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # App Settings
    debug: bool = False
    grace_period_minutes: int = 15
    slot_reservation_minutes: int = 10
    max_patients_per_day: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow case-insensitive field matching
        case_sensitive = False
        # Allow extra fields in .env without causing errors
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

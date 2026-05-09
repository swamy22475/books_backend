from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/schoolerp"
    SCHOOL_START_TIME: str = "09:00"  # HH:MM
    BIOMETRIC_MORNING_CUTOFF: str = "11:00"
    BIOMETRIC_AFTERNOON_CUTOFF: str = "12:00"
    DEFAULT_PERIODS: int = 6

    class Config:
        env_file = ".env"

settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "finora_db"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # JWT Configuration
    jwt_secret: str = "your-super-secret-jwt-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Encryption Configuration
    pan_encryption_key: str = "your-fernet-encryption-key-32-bytes-base64-encoded"

    # Application Configuration
    environment: str = "development"
    app_name: str = "Finora Backend API"
    app_version: str = "1.0.0"

    # OTP Configuration
    otp_length: int = 4
    otp_ttl_seconds: int = 120
    otp_max_attempts: int = 3
    otp_rate_limit_window_minutes: int = 10

    # CORS Configuration
    cors_origins: list[str] = ["*"]


settings = Settings()

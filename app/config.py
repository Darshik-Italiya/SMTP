from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Dental Patient Triage Email Service"

    # Application settings
    APP_NAME: str = "Dental Patient Triage Service"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Email settings
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "no-reply@dentalpatienttriage.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Dental Patient Triage Service")
    DEFAULT_FROM_EMAIL: str = os.getenv(
        "DEFAULT_FROM_EMAIL", "no-reply@dentalpatienttriage.com"
    )
    EMAIL_HOST_USER: str = os.getenv(
        "EMAIL_HOST_USER", "no-reply@dentalpatienttriage.com"
    )

    # SMTP.com API Settings
    SMTP_API_KEY: str = os.getenv("SMTP_API_KEY", "")
    SMTP_CHANNEL: str = os.getenv("SMTP_CHANNEL", "dentalpatienttriage_com")
    SMTP_API_URL: str = os.getenv("SMTP_API_URL", "https://api.smtp.com/v4/messages")

    # SMTP Server Settings (for direct SMTP)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "riverinadentalalbury@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    USE_TLS: bool = os.getenv("USE_TLS", "True").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def auth_headers(self) -> dict:
        """Return the authentication headers for SMTP.com API."""
        return {
            "Authorization": f"Bearer {self.SMTP_API_KEY}",
            "Content-Type": "application/json",
        }


# Create settings instance
settings = Settings()

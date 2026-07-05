from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SupportIQ AI"

    groq_api_key: str
    model_name: str = "llama-3.3-70b-versatile"

    database_url: str

    email_address: str
    email_password: str

    imap_server: str = "imap.gmail.com"
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587

    email_poll_interval_seconds: int = Field(default=60, ge=10)
    email_folder: str = "INBOX"

    max_attachment_size_mb: int = Field(default=10, gt=0)
    allowed_attachment_types: str = "pdf,png,jpg,jpeg,txt,docx"

    llm_timeout_seconds: int = Field(default=30, gt=0)
    llm_max_retries: int = Field(default=3, ge=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("allowed_attachment_types")
    @classmethod
    def normalize_attachment_types(cls, value: str) -> str:
        extensions = [
            extension.strip().lower().lstrip(".")
            for extension in value.split(",")
            if extension.strip()
        ]

        return ",".join(dict.fromkeys(extensions))

    @property
    def allowed_attachment_extensions(self) -> set[str]:
        return set(self.allowed_attachment_types.split(","))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

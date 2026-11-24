from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class CorsSettings(BaseModel):
    allow_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
        ],
    )
    allow_methods: list[str] = Field(
        default_factory=lambda: ["*"],
    )
    allow_headers: list[str] = Field(
        default_factory=lambda: ["*"],
    )
    allow_credentials: bool = True


class SecurityHeadersSettings(BaseModel):
    enabled: bool = True


class RequestSettings(BaseModel):
    max_body_size: int = 10 * 1024 * 1024


class HTTPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="HTTP_",
        env_nested_delimiter="__",
        extra="ignore",
        frozen=True,
    )

    server: ServerSettings = Field(
        default_factory=lambda: ServerSettings(),
    )

    cors: CorsSettings = Field(
        default_factory=lambda: CorsSettings(),
    )

    security_headers: SecurityHeadersSettings = Field(
        default_factory=lambda: SecurityHeadersSettings(),
    )

    request: RequestSettings = Field(
        default_factory=lambda: RequestSettings(),
    )

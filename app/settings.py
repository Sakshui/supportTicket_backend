from pathlib import Path
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env.local",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# --------------------------------------------------------------- APP ---------------------------------------------------------------
class AppSettings(CommonSettings):
    api_version: str    = "1.0.0"
    project_name: str   = Field(env="PROJECT_NAME")
    project_domain: str = Field(env="PROJECT_DOMAIN")
    

# -------------------------------------------------------------- SECURITY ----------------------------------------------------------
class SecuritySettings(CommonSettings):
    jwt_secret: str                   = Field(default="", env="JWT_SECRET")
    jwt_algorithm: str                = Field(default="HS256")
    access_token_expire_minutes: int  = Field(default=60 * 24) 
    refresh_token_expire_minutes: int = Field(default=60 * 2400) 
#

# --------------------------------------------------------------- CORS --------------------------------------------------------------
class CORSSettings(CommonSettings):
    allowed_origins: list[str] = Field(default=["*"])
    allowed_methods: list[str] = Field(default=["*"])
    allowed_headers: list[str] = Field(default=["*"])


# ----------------------------------------------------------------. AWS --------------------------------------------------------------
class AWSSettings(CommonSettings):
    aws_access_key_id: str       = Field(default="", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str   = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    aws_region_name: str         = Field(default="", env="AWS_REGION_NAME")
    aws_storage_bucket_name: str = Field(default="", env="AWS_STORAGE_BUCKET_NAME")

    @property
    def media_url(self) -> str:
        return f"https://s3.{self.aws_region_name}.amazonaws.com/{self.aws_storage_bucket_name}/media/"

    @property
    def static_url(self) -> str:
        return f"https://s3.{self.aws_region_name}.amazonaws.com/{self.aws_storage_bucket_name}/static/"
    

# ------------------------------------------------------------ EMAIL / SMTP -------------------------------------------------------
class EmailSettings(CommonSettings):
    smtp_host: str     = Field(default="", env="SMTP_HOST")
    smtp_port: int     = Field(default=587, env="SMTP_PORT")
    smtp_user: str     = Field(default="", env="SMTP_USER")
    smtp_password: str = Field(default="", env="SMTP_PASSWORD")
    from_email: str    = Field(default="", env="SMTP_FROM_EMAIL")
    use_tls: bool      = Field(default=True)


# --------------------------------------------------------------- CELERY ---------------------------------------------------------
class CelerySettings(CommonSettings):
    redis_host: str     = Field(default="localhost", env="REDIS_HOST")
    redis_port: int     = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_db: int       = Field(default=0)

    @property
    def broker_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def result_backend(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"


# -------------------------------------------------------------- DATABASE ----------------------------------------------------------
class DatabaseSettings(CommonSettings):

    # support_tickets DB
    support_tickets_db_user: str      = Field(default="", env="SUPPORT_TICKETS_DB_USER")
    support_tickets_db_name: str      = Field(default="", env="SUPPORT_TICKETS_DB_NAME")
    support_tickets_db_host: str      = Field(default="", env="SUPPORT_TICKETS_DB_HOST")
    support_tickets_db_port: str      = Field(default="", env="SUPPORT_TICKETS_DB_PORT")
    support_tickets_db_password: str  = Field(default="", env="SUPPORT_TICKETS_DB_PASSWORD")

    @property
    def support_tickets_url(self) -> str:
        return f"postgresql+asyncpg://{self.support_tickets_db_user}:{self.support_tickets_db_password}@{self.support_tickets_db_host}:{self.support_tickets_db_port}/{self.support_tickets_db_name}"
    
    @property
    def support_tickets_db_url_sync(self) -> str:
        return f"postgresql+psycopg2://{self.support_tickets_db_user}:{self.support_tickets_db_password}@{self.support_tickets_db_host}:{self.support_tickets_db_port}/{self.support_tickets_db_name}"


# --------------------------------------------------------------- MASTER SETTINGS ---------------------------------------------------
class Settings(CommonSettings):
    app: AppSettings           = Field(default_factory=AppSettings)
    aws: AWSSettings           = Field(default_factory=AWSSettings)
    db: DatabaseSettings       = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors: CORSSettings         = Field(default_factory=CORSSettings)
    email: EmailSettings       = Field(default_factory=EmailSettings)
    celery: CelerySettings     = Field(default_factory=CelerySettings)


@lru_cache()
def get_settings() -> Settings:
    return Settings()

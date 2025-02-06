from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "WhatsApp Recap API"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: str | List[str] = "*"
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin]
    
    # External Services
    MERCADOPAGO_ACCESS_TOKEN: str
    
    # Environment
    ENVIRONMENT: str = "development"

    # Payment Settings
    PAYER_EMAIL: str
    PAYER_FIRST_NAME: str
    PAYER_LAST_NAME: str
    PAYER_ID_TYPE: str
    PAYER_ID_NUMBER: str
    PAYER_ADDRESS: dict

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()

def clear_settings_cache():
    get_settings.cache_clear() 
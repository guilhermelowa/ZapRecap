from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    MERCADOPAGO_ACCESS_TOKEN: str
    # Add other configuration variables here

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()

# Add this function to clear the cache
def clear_settings_cache():
    get_settings.cache_clear() 
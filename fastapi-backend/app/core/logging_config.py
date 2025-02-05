import logging
from fastapi.logger import logger as fastapi_logger

def configure_logging():
    # Configure your logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Disable uvicorn access logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Optional: Disable other noisy loggers
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING) 
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, max_size: int = 100, expiration_minutes: int = 30):
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.max_size = max_size
        self.expiration = timedelta(minutes=expiration_minutes)

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp"""
        # Remove oldest item if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
            del self.cache[oldest_key]
            logger.info(f"Cache full, removed oldest item: {oldest_key}")

        self.cache[key] = (value, datetime.now())

    def get(self, key: str) -> Any:
        """Get value from cache if it exists and hasn't expired"""
        if key not in self.cache:
            return None

        value, timestamp = self.cache[key]
        if datetime.now() - timestamp > self.expiration:
            # Remove expired item
            del self.cache[key]
            logger.info(f"Removed expired cache item: {key}")
            return None

        return value

    def clear(self) -> None:
        """Clear all items from cache"""
        self.cache.clear()

import redis
import json
import logging
from typing import Optional


logger = logging.getLogger(__name__)

class FallbackQueue:
    
    def __init__(self,host="localhost",port=6379):
        
        try:
            self.redis_client = redis.Redis(
                host = host,
                port=port,
                db=1,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            
            self.redis_client.ping()
            self.is_healthy = True
            logger.info("Redis fallback queue initialized")
        except Exception as e:
            self.is_healthy = False
            logger.error("Redis fallback queue unavailable")
    
    def push(self, queue_name: str, message: dict) -> bool:
        """Push message to fallback queue"""
        try:
            self.redis_client.lpush(queue_name, json.dumps(message))
            logger.info(f"📦 Message pushed to fallback queue: {queue_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to push to fallback queue: {str(e)}")
            return False
        
    def pop(self, queue_name: str) -> Optional[dict]:
        """Pop message from fallback queue"""
        try:
            message = self.redis_client.rpop(queue_name)
            if message:
                return json.loads(message)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to pop from fallback queue: {str(e)}")
            return None
    
    def get_queue_length(self, queue_name: str) -> int:
        """Get number of messages in queue"""
        try:
            return self.redis_client.llen(queue_name)
        except:
            return 0

# Initialize fallback queue
fallback_queue = FallbackQueue()
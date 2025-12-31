import redis
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RedisCache:
    
    def __init__(self,host='localhost',port=6379,db=0):
        
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            max_connections=50
        )
        
        logger.info("Redis Cache initialized")
    
    
    def get(self, key:str) -> Optional[dict]:
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Redis Get Error: {str(e)}")
            return None
            
    def set(self,key:str,value:dict,ttl:int = 3600):
        
        try:
            self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Redis Set Error {str(e)}")
            return False
        
    def delete(self,key:str):
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis Delete error {str(e)}")
            return False



cache = RedisCache()

        
        
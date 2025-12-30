from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Message(BaseModel):
    topic: str
    key: Optional[str] = None
    value: str
    
class MessageResponse(BaseModel):
    status: str
    message: str
    timestamp: str

class KafkaMessage(BaseModel):
    topic: str
    partition: int
    offset: int
    key: Optional[str]
    value: str
    timestamp: str
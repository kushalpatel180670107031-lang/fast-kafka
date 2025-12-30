from fastapi import APIRouter, HTTPException
from app.schemas.kafka_models import Message, MessageResponse, KafkaMessage
from app.features.kafka_producer import Producer
from app.features.kafka_consumer import Consumer
from datetime import datetime
from typing import List

router = APIRouter()

producer = Producer()
consumer = Consumer()

@router.post("/produce", response_model=MessageResponse)
async def produce_message(message: Message):
    """Send a message to Kafka topic"""
    try:
        result = producer.send_message(
            topic=message.topic,
            value={"data": message.value},
            key=message.key
        )
        
        if result["status"] == "success":
            return MessageResponse(
                status="success",
                message=f"Message sent to topic '{message.topic}'",
                timestamp=datetime.now().isoformat()
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/consume/{topic}", response_model=List[KafkaMessage])
async def consume_messages(topic: str, max_messages: int = 10, group_id: str = "fastapi-consumer"):
    """Consume messages from a Kafka topic"""
    try:
        messages = consumer.consume_messages(topic, group_id, max_messages)
        
        return [
            KafkaMessage(
                topic=msg["topic"],
                partition=msg["partition"],
                offset=msg["offset"],
                key=msg["key"],
                value=str(msg["value"]),
                timestamp=datetime.fromtimestamp(msg["timestamp"]/1000).isoformat()
            )
            for msg in messages
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics/{topic}/info")
async def get_topic_info(topic: str):
    """Get information about a Kafka topic"""
    try:
        info = consumer.get_topic_info(topic)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "FastAPI Kafka Integration"}
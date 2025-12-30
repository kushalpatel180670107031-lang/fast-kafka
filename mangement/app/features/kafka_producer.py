from kafka import KafkaProducer
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Producer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        logger.info("Kafka Producer initialized")
    
    def send_message(self, topic: str, value: dict, key: str = None):
        try:
            future = self.producer.send(topic, key=key, value=value)
            record_metadata = future.get(timeout=10)
            logger.info(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
            return {
                "status": "success",
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset
            }
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def close(self):
        self.producer.close()
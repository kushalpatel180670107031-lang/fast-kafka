from kafka import KafkaProducer
import json
import logging
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# class Producer:
#     def __init__(self, bootstrap_servers=['localhost:9092']):
#         self.producer = KafkaProducer(
#             bootstrap_servers=bootstrap_servers,
#             value_serializer=lambda v: json.dumps(v).encode('utf-8'),
#             key_serializer=lambda k: k.encode('utf-8') if k else None
#         )
#         logger.info("Kafka Producer initialized")
    
#     def send_message(self, topic: str, value: dict, key: str = None):
#         try:
#             future = self.producer.send(topic, key=key, value=value)
#             record_metadata = future.get(timeout=10)
#             logger.info(f"Message sent to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
#             return {
#                 "status": "success",
#                 "topic": record_metadata.topic,
#                 "partition": record_metadata.partition,
#                 "offset": record_metadata.offset
#             }
#         except Exception as e:
#             logger.error(f"Error sending message: {str(e)}")
#             return {"status": "error", "message": str(e)}
    
#     def close(self):
#         self.producer.close()
        
    

class Producer:
    
    def __init__(self,bootstrap_server=['localhost:9092']):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_server,
            value_serializer = lambda v: json.dumps(v).encode('utf-8'),
            key_serializer = lambda k: k.encode('utf-8') if k else None,
            # High throughput settings
            acks=1,  # Leader acknowledgment only (faster)
            compression_type='snappy',  # Compress messages
            batch_size=32768,  # 32KB batches
            linger_ms=10,  # Wait 10ms to batch messages
            buffer_memory=67108864,  # 64MB buffer
            max_in_flight_requests_per_connection=5,
            retries=3,
            request_timeout_ms=30000
        )
        logger.info("High-throughput Kafka Producer initialized")
        
    def send_message_async(self, topic: str, value: dict, key: str = None):
        """Non-blocking send - returns immediately"""
        try:
            future = self.producer.send(topic, key=key, value=value)
            # Don't wait for acknowledgment - return immediately
            return {"status": "queued", "message": "Message queued successfully"}
        except KafkaError as e:
            logger.error(f"Kafka error: {str(e)}")
            raise Exception(f"Failed to queue message: {str(e)}")
    
    def flush(self):
        """Force send all buffered messages"""
        self.producer.flush()
    
    def close(self):
        self.producer.close()
from kafka import KafkaProducer
import json
import logging
from kafka.errors import KafkaError,NoBrokersAvailable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

        
class Producer:
    
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.is_healthy = False
        self._initialize_producer()
    
    def _initialize_producer(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks=1,
                compression_type='snappy',
                batch_size=32768,
                linger_ms=10,
                buffer_memory=67108864,
                max_in_flight_requests_per_connection=5,
                retries=3,
                request_timeout_ms=10000,  # 10 seconds timeout
                connections_max_idle_ms=540000
            )
            self.is_healthy = True
            logger.info("Kafka Producer initialized successfully")
        except NoBrokersAvailable:
            self.is_healthy = False
            logger.error("Kafka brokers not available")
        except Exception as e:
            self.is_healthy = False
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            
    def health_check(self) -> bool:
        """Check if Kafka is healthy"""
        if not self.producer:
            return False
        
        try:
            # Try to get cluster metadata
            self.producer.bootstrap_connected()
            self.is_healthy = True
            return True
        except:
            self.is_healthy = False
            return False
    
    
    def send_message_async(self, topic: str, value: dict, key: str = None):
        """Send message with automatic fallback"""
        
        # Check if Kafka is healthy
        if not self.is_healthy or not self.producer:
            logger.warning("Kafka is down, attempting reconnection...")
            self._initialize_producer()
        
        # If still not healthy, raise exception (will trigger fallback)
        if not self.is_healthy:
            raise KafkaError("Kafka is unavailable")
        
        try:
            future = self.producer.send(topic, key=key, value=value)
            # Don't wait for response (async)
            return {"status": "queued", "message": "Message queued to Kafka"}
        
        except KafkaError as e:
            self.is_healthy = False
            logger.error(f"Kafka send failed: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise e
    
    def close(self):
        if self.producer:
            try:
                self.producer.flush()
                self.producer.close()
            except:
                pass
  

# class Producer:
    
#     def __init__(self,bootstrap_server=['localhost:9092']):
#         self.producer = KafkaProducer(
#             bootstrap_servers=bootstrap_server,
#             value_serializer = lambda v: json.dumps(v).encode('utf-8'),
#             key_serializer = lambda k: k.encode('utf-8') if k else None,
#             # High throughput settings
#             acks=1,  # Leader acknowledgment only (faster)
#             compression_type='snappy',  # Compress messages
#             batch_size=32768,  # 32KB batches
#             linger_ms=10,  # Wait 10ms to batch messages
#             buffer_memory=67108864,  # 64MB buffer
#             max_in_flight_requests_per_connection=5,
#             retries=3,
#             request_timeout_ms=30000
#         )
#         logger.info("High-throughput Kafka Producer initialized")
        
#     def send_message_async(self, topic: str, value: dict, key: str = None):
#         """Non-blocking send - returns immediately"""
#         try:
#             future = self.producer.send(topic, key=key, value=value)
#             # Don't wait for acknowledgment - return immediately
#             return {"status": "queued", "message": "Message queued successfully"}
#         except KafkaError as e:
#             logger.error(f"Kafka error: {str(e)}")
#             raise Exception(f"Failed to queue message: {str(e)}")
    
#     def flush(self):
#         """Force send all buffered messages"""
#         self.producer.flush()
    
#     def close(self):
#         self.producer.close()
        





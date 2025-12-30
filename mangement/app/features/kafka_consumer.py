from kafka import KafkaConsumer, TopicPartition
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Consumer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
        self.bootstrap_servers = bootstrap_servers
        logger.info("Kafka Consumer manager initialized")
    
    def consume_messages(self, topic: str, group_id: str = "fastapi-consumer", max_messages: int = 10):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=group_id,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                consumer_timeout_ms=5000
            )
            
            messages = []
            count = 0
            
            for message in consumer:
                if count >= max_messages:
                    break
                    
                messages.append({
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "key": message.key.decode('utf-8') if message.key else None,
                    "value": message.value,
                    "timestamp": message.timestamp
                })
                count += 1
            
            consumer.close()
            return messages
            
        except Exception as e:
            logger.error(f"Error consuming messages: {str(e)}")
            return []
    
    def get_topic_info(self, topic: str):
        try:
            consumer = KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                consumer_timeout_ms=1000
            )
            
            partitions = consumer.partitions_for_topic(topic)
            
            if partitions:
                info = {
                    "topic": topic,
                    "partitions": list(partitions),
                    "partition_count": len(partitions)
                }
            else:
                info = {"topic": topic, "exists": False}
            
            consumer.close()
            return info
            
        except Exception as e:
            logger.error(f"Error getting topic info: {str(e)}")
            return {"error": str(e)}
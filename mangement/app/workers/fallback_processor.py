import time
import logging
from app.features.fallback_queue import fallback_queue
from app.features.kafka_producer import Producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_fallback_queue():
    producer = Producer()
    queue_name = "product-fallback-queue"
    logger.info("🔄 Fallback queue processor started")
    
    while True:
        try:
            # Check if Kafka is back online
            if not producer.health_check():
                logger.warning("Kafka still down, waiting...")
                time.sleep(10)
                continue
            
            # Get queue depth
            queue_depth = fallback_queue.get_queue_length(queue_name)
            
            if queue_depth > 0:
                logger.info(f"📦 Processing {queue_depth} messages from fallback queue")
                
                # Process messages in batches
                processed = 0
                failed = 0
                
                for _ in range(min(queue_depth, 100)):  # Process max 100 at a time
                    message = fallback_queue.pop(queue_name)
                    
                    if not message:
                        break
                    
                    try:
                        # Send to Kafka
                        producer.send_message_async(
                            topic="product-uploads",
                            value=message,
                            key=message.get("product_id")
                        )
                        processed += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to process message: {str(e)}")
                        # Put it back in queue
                        fallback_queue.push(queue_name, message)
                        failed += 1
                        break  # Stop processing if Kafka fails
                
                logger.info(f"✅ Processed: {processed}, Failed: {failed}")
            
            # Sleep before next check
            time.sleep(5)
            
        except KeyboardInterrupt:
            logger.info("Fallback processor stopped")
            break
        except Exception as e:
            logger.error(f"Error in fallback processor: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    process_fallback_queue()
from kafka import KafkaConsumer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.products import ProductRecord
from app.schemas.product import ProductStatus
from app.db.session import Base,SessionLocal
from app.core.config import settings
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def process_product_message(message_value):
    session = SessionLocal()
    try:
        product_data = message_value
        
        new_product = ProductRecord(
            name = product_data.get("name"),
            price = product_data.get("price"),
            image_url = product_data.get("image_url")
        
        )
        
        session.add(new_product)
        session.commit()
        
        # Simulate processing (image optimization, validation, etc.)
        # time.sleep(0.1)  # Remove in production
        
        # Update status to completed
        # new_product.status = ProductStatus.COMPLETED
        # session.commit()
        
        logger.info(f"Product {product_data['product_id']} processed successfully")

    except Exception as e:
        logger.error(f"")
        session.rollback()
    
    # if new_product:
    #     new_product.status = ProductStatus.FAILED
    #     session.commit()
    finally:
        session.close()


def start_consumer():
    
    consumer = KafkaConsumer(
        "product-uploads",
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='product-processor-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        # High throughput settings
        max_poll_records=500,  # Process 500 messages at a time
        session_timeout_ms=30000,
        max_poll_interval_ms=300000
    )
    logger.info("Kafka consumer started - waiting for messages...")
    try:
        for message in consumer:
            process_product_message(message.value)
    except KeyboardInterrupt:
        logger.info("Consumer stopped")
    finally:
        consumer.close()

if __name__ == "__main__":
    
    # Start consuming
    start_consumer()
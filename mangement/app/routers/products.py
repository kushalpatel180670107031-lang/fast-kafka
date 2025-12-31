
from fastapi import FastAPI,APIRouter, Depends,Request, HTTPException,BackgroundTasks
from app.schemas.product import ProductCreate,ProductResponse
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.models.products import ProductRecord
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
import json
from app.schemas.product import ProductCreate
from app.core.config import settings
from app.features.kafka_consumer import Consumer
from app.features.kafka_producer import Producer
import uuid
import logging
from sqlalchemy import select
logger = logging.getLogger(__name__)

router = APIRouter()
producer = Producer()


@router.post("/process-product", response_model=ProductResponse)
async def process_product(product: ProductCreate,background_tasks:BackgroundTasks):
    

    """
    Fast endpoint - just queue the message to Kafka
    NO database writes here!
    """
    product_id = str(uuid.uuid4())
    
    payload = {
        "product_id":product_id,
        "name":product.name,
        "price":product.price,
        "image_url":product.image_url,
        "event_type":"PRODUCT_UPLOADED",
        "timestamp":str(datetime.utcnow())
    }
    
    try:
        result = producer.send_message_async(
            topic="product-uploads",
            value = payload,
            key=product_id
        )
        logger.info(f"Product {product_id} queued Successfully!")
        
        return ProductResponse(
            message="Product upload accepted",
            status="queued",
            product_id=product_id,
            queue_position="Processing in background"
        )
        
    except Exception as e:
        logger.error(f"Failed to queue product : {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please retry."
        )
        

@router.get("/product-status/{product_id}")
async def get_product_status(
    product_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(
        select(ProductRecord).where(ProductRecord.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        return {
            "status":"not_found",
            "message":"Product not found or still in queue"
        }

    return {
        "product_id":product_id,
        "status":"done",
        "name":product.name,
        "created_at":product.created_at
    }






    
    
# @router.post("/process-product")
# async def process_product(
#     product: ProductCreate,
#     db: AsyncSession = Depends(get_async_db)
# ):
#     payload = {
#         "name": product.name,
#         "price": product.price,
#         "image_url": product.image_url,
#         "event_type": "PRODUCT_UPLOADED"
#     }

#     new_product = ProductRecord(
#         name=product.name,
#         price=product.price,
#         image_url=product.image_url
#     )

#     try:
#         db.add(new_product)
#         await db.commit()        # commit within try/except
#         await db.refresh(new_product)
#     except Exception as e:
#         await db.rollback()      # rollback on failure
#         raise e

#     return {"message": "Accepted", "status": "In Queue"}



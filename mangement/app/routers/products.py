
from fastapi import FastAPI,APIRouter, Depends,Request, HTTPException,BackgroundTasks
from app.schemas.product import ProductCreate,ProductResponse
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.models.products import ProductRecord
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
import json
from app.schemas.product import ProductCreate,ProductDetail
from app.core.config import settings
from app.features.kafka_consumer import Consumer
from app.features.kafka_producer import Producer
import uuid
import logging
from sqlalchemy import select
from app.features.redis_cache import cache
from app.features.fallback_queue import fallback_queue
from app.features.database_fallback  import direct_db_write
from typing import Optional
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

router = APIRouter()

producer = Producer()

system_health = {
    "kafka": True,
    "redis": True,
    "database": True
}

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
        
        system_health["kafka"] = True
        logger.info(f"Product {product_id} queued Successfully!")
        
        return ProductResponse(
            message="Product upload accepted",
            status="queued",
            product_id=product_id,
            queue_position="Processing in background"
        )
        
    except Exception as e:
        system_health["kafka"] = False
        logger.error(f"Failed to queue product : {str(e)}")
        
        # raise HTTPException(
        #     status_code=503,
        #     detail="Service temporarily unavailable. Please retry."
        # )

        try:
            if fallback_queue.is_healthy and fallback_queue.push("product-fallback-queue", payload):
                system_health["redis"] = True
                logger.info(f"📦 Product {product_id} queued to Redis fallback")
                return ProductResponse(
                    message="Product upload accepted (fallback mode)",
                    status="queued_redis",
                    product_id=product_id,
                    queue_position="Processing via fallback queue"
                )
        except Exception as redis_error:
            system_health["redis"] = False
            logger.warning(f"Redis fallback failed: {str(redis_error)}")
        
        # TIER 3: Last Resort - Direct Database Write
        try:
            if direct_db_write(payload):
                system_health["database"] = True
                logger.warning(f"Product {product_id} written directly to database")
                
                return ProductResponse(
                    message="Product upload accepted (direct write)",
                    status="completed_direct",
                    product_id=product_id,
                    queue_position="Processed immediately"
                )
        
        except Exception as db_error:
            system_health["database"] = False
            logger.error(f"All systems failed: DB error: {str(db_error)}")
        
        # TIER 4: Complete Failure
        raise HTTPException(
            status_code=503,
            detail={
                "error": "All processing systems unavailable",
                "message": "Please retry in a few moments",
                "product_id": product_id,
                "retry_after": 30
            }
        )
            
            
        

@router.get("/product-status/{product_id}")
async def get_product_status(
    product_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    
    cache_key = f"product:{product_id}"
    cached_product = cache.get(cache_key)
    if cached_product:
        logger.info(f"Cache HIT for {product_id}")
        cached_product["from_cache"] = True
        return ProductDetail(**cached_product)
    logger.info(f"Cache MISS for {product_id}")
    
    try:
        result = await db.execute(
            select(ProductRecord).where(ProductRecord.id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
        product_data = {
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url,
            "created_at": product.created_at.isoformat()
        }
        cache.set(cache_key, product_data, ttl=3600)
        product_data["from_cache"] = False
        return ProductDetail(**product_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")






@router.get("/products")
async def get_all_products(
    page: int = 1,
    page_size: int = 20,
    name: Optional[str]=None,
    db: AsyncSession= Depends(get_async_db)
):
    
    if page < 1:
        raise HTTPException(status_code=400,detail= " Page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400,detail= "Page size must between 1 and 100")

    try:
        query = select(ProductRecord)
        if name:
            query = query.where(ProductRecord.name.ilike(f"%{name}%"))
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total_items = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.order_by(ProductRecord.created_at.desc()).offset(offset).limit(page_size)
        
        
        result = await db.execute(query)
        products = result.scalars().all()
        products_list = [
            {
                "product_id": p.id,
                "name": p.name,
                "price": p.price,
                "image_url": p.image_url,
                "description":p.name,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat()
            }
            for p in products
        ]
        total_pages = (total_items + page_size - 1) // page_size
        
        return {
            "products": products_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "filters": {
                "name": name,
                
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")



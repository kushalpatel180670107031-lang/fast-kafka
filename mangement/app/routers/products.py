
from fastapi import FastAPI,APIRouter, Depends,Request, HTTPException
from app.schemas.product import ProductCreate
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.models.products import ProductRecord
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
import json
from app.schemas.product import ProductCreate
from app.core.config import settings
from app.core.kefka_config import PRODUCER,kafka_serializer
router = APIRouter()


    
    
@router.post("/process-product")
async def process_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db)
):
    payload = {
        "name": product.name,
        "price": product.price,
        "image_url": product.image_url,
        "event_type": "PRODUCT_UPLOADED"
    }

    new_product = ProductRecord(
        name=product.name,
        price=product.price,
        image_url=product.image_url
    )

    try:
        db.add(new_product)
        await db.commit()        # commit within try/except
        await db.refresh(new_product)
    except Exception as e:
        await db.rollback()      # rollback on failure
        raise e

    return {"message": "Accepted", "status": "In Queue"}



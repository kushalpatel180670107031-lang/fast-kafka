from app.core.config import settings
from app.db.session import Base, async_session_pool
from app.models.products import ProductRecord
from sqlalchemy import select
import pandas as pd
import requests
from PIL import Image
import os
from io import BytesIO

async def get_all_product():
    async with async_session_pool() as db :
        try:
            result = await db.execute(
                select(ProductRecord.id,ProductRecord.name,ProductRecord.image_url)
            )
            products = result.mappings().all()
            
            return products
            
        except Exception as e:
            raise RuntimeError(f"DB error while fetching products: {e}")
        
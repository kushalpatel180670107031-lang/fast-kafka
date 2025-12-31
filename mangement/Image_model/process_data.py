from app.core.config import settings
from app.db.session import Base, async_session_pool
from app.models.products import ProductRecord
from sqlalchemy import select
import pandas as pd
import requests
from PIL import Image
import os
from io import BytesIO
from get_data import get_all_product
from validate_data import is_valid_image,download_image
import asyncio







products = asyncio.run(get_all_product())
# print(products)



valid_datas = []

for product in products:
    
    print(product)
    image_url = product.get("image_url")
    if image_url == "http://example.com/image.jpg":
        continue
    if is_valid_image(image_url):
        valid_datas.append(product)
    

df = pd.DataFrame(valid_datas)
print(df.head())

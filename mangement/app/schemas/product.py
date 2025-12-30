
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: float
    image_url: str
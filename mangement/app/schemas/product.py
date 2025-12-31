
from pydantic import BaseModel,Field
import enum

class ProductCreate(BaseModel):
    name: str
    price: float
    image_url: str
    
    
class ProductResponse(BaseModel):
    message: str
    status: str
    product_id: str
    queue_position: str

class ProductStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
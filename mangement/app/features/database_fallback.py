from app.schemas.product import ProductStatus
from app.models.products import ProductRecord
from app.db.session import SessionLocal
import logging

logger = logging.getLogger(__name__)


def direct_db_write(product_data:dict):
    session = SessionLocal()
    try:
        new_product = ProductRecord(
            name=product_data["name"],
            price=product_data["price"],
            image_url=product_data["image_url"],
        )
        
        session.add(new_product)
        session.commit()
        
        logger.warning(f"⚠️ EMERGENCY: Product {product_data['product_id']} written directly to DB")
        return True
        
    except Exception as e:
        logger.error(f"❌ Direct DB write failed: {str(e)}")
        session.rollback()
        return False
    finally:
        session.close()
    
    
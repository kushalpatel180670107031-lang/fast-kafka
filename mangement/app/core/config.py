
import os 
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env
load_dotenv()

class Setting():
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "postgresql")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")

    # Sync connection string
    DB_URI: str = os.getenv(
        "DATABASE_URL",
        f"{DB_SCHEMA}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )

    # Async connection string
    ASYNC_DB_URI: str = (
        f"{DB_SCHEMA}+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    # app/core/config.py
    # Sync: Used by standard scripts and migrations
    DB_URI = "postgresql://mangement:1234@localhost:5432/mangement-stg"
    # Async: Used by FastAPI for high-concurrency
    ASYNC_DB_URI = "postgresql+asyncpg://mangement:1234@localhost:5432/mangement-stg"
    
    KAFKA_TOPIC:str = os.getenv('KAFKA_TOPIC')
    KAFKA_CONSUMER_GROUP_PREFIX:str = os.getenv('KAFKA_CONSUMER_GROUP_PREFIX', 'group')
    KAFKA_BOOTSTRAP_SERVERS:str = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    
    
settings = Setting()
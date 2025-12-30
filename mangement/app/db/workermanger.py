import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.workers.consumer_worker import consume_and_save # Import your worker function

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # Start the Kafka consumer as a background task
    task = asyncio.create_task(consume_and_save())
    print("Kafka Consumer started...")
    
    yield  # The app stays here while running
    
    # --- SHUTDOWN ---
    task.cancel()
    print("Kafka Consumer stopped.")

app = FastAPI(lifespan=lifespan)
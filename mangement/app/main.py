from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.products import router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FastAPI Kafka Integration",
    description="FastAPI backend with Kafka producer and consumer",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["kafka"])

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application started")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application shutting down")

@app.get("/")
async def root():
    return {
        "message": "FastAPI Kafka Integration API",
        "docs": "/docs",
        "kafka_ui": "http://localhost:8080"
    }
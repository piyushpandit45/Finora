from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class Database:
    client: Optional[AsyncIOMotorClient] = None

    async def connect(self) -> None:
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_url)
            logger.info(f"Connected to MongoDB at {settings.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def init_beanie(self, document_models) -> None:
        try:
            await init_beanie(
                database=self.client[settings.database_name],
                document_models=document_models
            )
            logger.info(f"Beanie initialized with {len(document_models)} document models")
        except Exception as e:
            logger.error(f"Failed to initialize Beanie: {e}")
            raise


database = Database()

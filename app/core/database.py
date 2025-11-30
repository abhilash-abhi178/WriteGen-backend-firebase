"""MongoDB database connection using Motor."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings


class Database:
    """MongoDB database connection manager."""
    
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db = Database()


async def connect_to_mongodb() -> None:
    """Connect to MongoDB database."""
    settings = get_settings()
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.db = db.client[settings.mongodb_database]


async def close_mongodb_connection() -> None:
    """Close MongoDB database connection."""
    if db.client:
        db.client.close()


def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance."""
    return db.db

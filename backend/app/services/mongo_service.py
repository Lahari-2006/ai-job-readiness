"""
MongoDB Service
Saves every analysis result to MongoDB for history tracking.
"""

import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global client instance
_client = None
_db = None


def get_db():
    """Get MongoDB database instance."""
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
        _db = _client[settings.MONGODB_DB]
    return _db


async def save_analysis(result: dict, resume_filename: str) -> str:
    """
    Save analysis result to MongoDB.
    Returns the inserted document ID as string.
    """
    try:
        db = get_db()
        document = {
            **result,
            "resume_filename": resume_filename,
            "created_at": datetime.utcnow(),
        }
        inserted = await db.analyses.insert_one(document)
        logger.info(f"Saved analysis to MongoDB: {inserted.inserted_id}")
        return str(inserted.inserted_id)

    except Exception as e:
        logger.warning(f"MongoDB save failed (non-fatal): {e}")
        return None


async def get_all_analyses() -> list:
    """Fetch all past analyses from MongoDB."""
    try:
        db = get_db()
        cursor = db.analyses.find().sort("created_at", -1).limit(50)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # convert ObjectId to string
            results.append(doc)
        return results
    except Exception as e:
        logger.warning(f"MongoDB fetch failed: {e}")
        return []
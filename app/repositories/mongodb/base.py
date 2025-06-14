import logging
from typing import Any, List, Optional, Type, TypeVar

from pydantic import BaseModel

from app.db.mongodb.mongodb import MongoDB
from app.repositories.interfaces.base import IRepository

T = TypeVar("T", bound=BaseModel)


class MongoDBRepository(IRepository[T]):
    """Base MongoDB repository implementation."""

    def __init__(self, model: Type[T], collection_name: str):
        self.model = model
        self.collection_name = collection_name
        self.collection = None
        self.logger = logging.getLogger(__name__)

    async def _get_collection(self):
        """Get MongoDB collection."""
        try:
            if self.collection is None:
                db = await MongoDB.get_database()
                self.collection = db[self.collection_name]
                self.logger.info(f"Connected to collection: {self.collection_name}")
            return self.collection
        except Exception as e:
            self.logger.error(f"Failed to get collection {self.collection_name}: {str(e)}")
            raise Exception(f"Failed to get collection {self.collection_name}: {str(e)}")

    async def create(self, obj_in: dict) -> T:
        """Create a new record in MongoDB."""
        try:
            collection = await self._get_collection()
            result = await collection.insert_one(obj_in)
            created_obj = await collection.find_one({"_id": result.inserted_id})
            return self.model(**created_obj)
        except Exception as e:
            self.logger.error(f"Failed to create record: {str(e)}")
            raise Exception(f"Failed to create record: {str(e)}")

    async def get(self, id: Any) -> Optional[T]:
        """Get a single record by id."""
        try:
            collection = await self._get_collection()
            obj = await collection.find_one({"_id": id})
            return self.model(**obj) if obj else None
        except Exception as e:
            self.logger.error(f"Failed to get record: {str(e)}")
            raise Exception(f"Failed to get record: {str(e)}")

    async def get_multi(self, *, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """Get multiple records with optional filtering and pagination."""
        try:
            collection = await self._get_collection()
            cursor = collection.find(filters).skip(skip).limit(limit)
            return [self.model(**doc) async for doc in cursor]
        except Exception as e:
            self.logger.error(f"Failed to get multiple records: {str(e)}")
            raise Exception(f"Failed to get multiple records: {str(e)}")

    async def update(self, id: Any, obj_in: dict) -> Optional[T]:
        """Update a record."""
        try:
            collection = await self._get_collection()
            await collection.update_one({"_id": id}, {"$set": obj_in})
            updated_obj = await collection.find_one({"_id": id})
            return self.model(**updated_obj) if updated_obj else None
        except Exception as e:
            self.logger.error(f"Failed to update record: {str(e)}")
            raise Exception(f"Failed to update record: {str(e)}")

    async def delete(self, id: Any) -> bool:
        """Delete a record."""
        try:
            collection = await self._get_collection()
            result = await collection.delete_one({"_id": id})
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Failed to delete record: {str(e)}")
            raise Exception(f"Failed to delete record: {str(e)}")

    async def exists(self, **filters) -> bool:
        """Check if a record exists with given filters."""
        try:
            collection = await self._get_collection()
            return await collection.count_documents(filters) > 0
        except Exception as e:
            self.logger.error(f"Failed to check record existence: {str(e)}")
            raise Exception(f"Failed to check record existence: {str(e)}")

    async def filter_one(self, **filters) -> Optional[T]:
        """Filter records with given filters."""
        try:
            collection = await self._get_collection()
            obj = await collection.find_one(filters)
            return self.model(**obj) if obj else None
        except Exception as e:
            self.logger.error(f"Failed to filter records: {str(e)}")
            raise Exception(f"Failed to filter records: {str(e)}")

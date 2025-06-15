import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from pydantic import BaseModel

from app.db.mongodb.mongodb import MongoDB


class PDFMetadata(BaseModel):
    """PDF metadata model."""

    id: str
    user_id: int
    filename: str
    title: str
    upload_date: datetime
    file_id: str
    parsed: bool = False
    text_content: Optional[str] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat(), ObjectId: lambda v: str(v)}


class PDFRepository:
    def __init__(self):
        self.mongodb = MongoDB()
        self.collection_name = "pdf_metadata"
        self.selected_pdf_collection_name = "selected_pdfs"
        self.fs: Optional[AsyncIOMotorGridFSBucket] = None
        self.logger = logging.getLogger(__name__)

    async def _get_fs(self) -> AsyncIOMotorGridFSBucket:
        """Get GridFS bucket instance."""
        try:
            if self.fs is None:
                db = await self.mongodb.get_database()
                self.fs = AsyncIOMotorGridFSBucket(db)
            return self.fs
        except Exception as e:
            self.logger.error(f"Failed to get GridFS bucket: {str(e)}")
            raise

    async def _get_collection(self):
        """Get MongoDB collection."""
        try:
            db = await self.mongodb.get_database()
            return db[self.collection_name]
        except Exception as e:
            self.logger.error(f"Failed to get collection: {str(e)}")
            raise

    async def _get_selected_pdf_collection(self):
        """Get MongoDB collection for selected PDFs."""
        try:
            db = await self.mongodb.get_database()
            return db[self.selected_pdf_collection_name]
        except Exception as e:
            self.logger.error(f"Failed to get selected PDF collection: {str(e)}")
            raise

    async def upload_pdf(self, user_id: int, filename: str, title: str, file_content: bytes) -> PDFMetadata:
        """Upload a PDF file to GridFS and store its metadata."""
        try:
            # Get database and GridFS
            fs = await self._get_fs()

            # Upload file to GridFS
            file_id = await fs.upload_from_stream(filename, file_content, metadata={"content_type": "application/pdf"})

            # Create metadata document
            metadata = {
                "id": str(ObjectId()),
                "user_id": user_id,
                "filename": filename,
                "title": title,
                "upload_date": datetime.utcnow(),
                "file_id": str(file_id),
                "parsed": False,
                "text_content": None,
            }

            # Insert metadata
            collection = await self._get_collection()
            await collection.insert_one(metadata)

            # Return metadata
            return PDFMetadata(**metadata)

        except Exception as e:
            self.logger.error(f"Failed to upload PDF: {str(e)}")
            raise

    async def get_user_pdfs(self, user_id: int) -> List[PDFMetadata]:
        """Get all PDFs uploaded by a specific user."""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"user_id": user_id})

            pdfs = []
            async for doc in cursor:
                # Convert MongoDB document to dictionary
                pdf_dict = {
                    "id": str(doc["_id"]),
                    "user_id": doc["user_id"],
                    "filename": doc["filename"],
                    "title": doc["title"],
                    "upload_date": doc["upload_date"],
                    "file_id": doc["file_id"],
                    "parsed": doc.get("parsed", False),
                    "text_content": doc.get("text_content"),
                }
                pdfs.append(PDFMetadata(**pdf_dict))

            return pdfs

        except Exception:
            self.logger.error(f"Failed to get user PDFs: {str(e)}")
            raise

    async def get_pdf_metadata(self, pdf_id: str) -> Optional[PDFMetadata]:
        """Get PDF metadata by ID."""
        try:
            collection = await self._get_collection()
            doc = await collection.find_one({"_id": ObjectId(pdf_id)})
            if doc:
                return PDFMetadata(
                    **{
                        "id": str(doc["_id"]),
                        "user_id": doc["user_id"],
                        "filename": doc["filename"],
                        "title": doc["title"],
                        "upload_date": doc["upload_date"],
                        "file_id": doc["file_id"],
                        "parsed": doc.get("parsed", False),
                        "text_content": doc.get("text_content"),
                    }
                )
            return None
        except Exception as e:
            self.logger.error(f"Failed to get PDF metadata: {str(e)}")
            raise

    async def get_pdf_file(self, file_id: str) -> Optional[bytes]:
        """Get PDF file content from GridFS."""
        try:
            fs = await self._get_fs()
            grid_out = await fs.open_download_stream(ObjectId(file_id))
            return await grid_out.read()
        except Exception as e:
            self.logger.error(f"Failed to get PDF file: {str(e)}")
            raise

    async def update_pdf_text(self, pdf_id: str, text_content: str) -> bool:
        """Update PDF text content."""
        try:
            collection = await self._get_collection()
            result = await collection.update_one({"_id": ObjectId(pdf_id)}, {"$set": {"text_content": text_content, "parsed": True}})
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Failed to update PDF text: {str(e)}")
            raise

    async def delete_pdf(self, file_id: str) -> bool:
        """Delete a PDF file from GridFS and its metadata."""
        fs = await self._get_fs()
        try:
            await fs.delete(ObjectId(file_id))
            return await self.delete(file_id)
        except Exception as e:
            self.logger.error(f"Failed to delete file from GridFS: {str(e)}")
            return False

    async def set_selected_pdf(self, user_id: int, pdf_id: str) -> bool:
        """Set the selected PDF for a user."""
        try:
            collection = await self._get_selected_pdf_collection()
            # Use upsert to either update existing or create new
            await collection.update_one({"user_id": user_id}, {"$set": {"pdf_id": pdf_id, "updated_at": datetime.utcnow()}}, upsert=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to set selected PDF: {str(e)}")
            return False

    async def get_selected_pdf(self, user_id: int) -> Optional[str]:
        """Get the selected PDF ID for a user."""
        try:
            collection = await self._get_selected_pdf_collection()
            doc = await collection.find_one({"user_id": user_id})
            return doc["pdf_id"] if doc else None
        except Exception as e:
            self.logger.error(f"Failed to get selected PDF: {str(e)}")
            return None

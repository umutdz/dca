import io
import logging
from typing import List, Optional

import PyPDF2
from fastapi import UploadFile

from app.repositories.mongodb.pdf import PDFMetadata, PDFRepository


class PDFService:
    def __init__(self):
        self.pdf_repository = PDFRepository()
        self.logger = logging.getLogger(__name__)

    async def upload_pdf(self, title: str, filename: str, file: UploadFile, user_id: int) -> PDFMetadata:
        """Upload a PDF file to MongoDB GridFS and store its metadata."""
        try:
            # Read file content
            file_content = await file.read()

            # Upload to MongoDB
            metadata = await self.pdf_repository.upload_pdf(user_id=user_id, filename=filename, title=title, file_content=file_content)

            return metadata
        except Exception as e:
            self.logger.error(f"Failed to upload PDF: {str(e)}")
            raise

    async def get_user_pdfs(self, user_id: int) -> List[PDFMetadata]:
        """Get all PDFs uploaded by a specific user."""
        try:
            pdfs = await self.pdf_repository.get_user_pdfs(user_id)
            self.logger.info(f"Retrieved {len(pdfs)} PDFs for user {user_id}")
            return pdfs
        except Exception as e:
            self.logger.error(f"Failed to get user PDFs: {str(e)}")
            raise

    async def parse_pdf(self, pdf_id: str) -> bool:
        """Extract and save text content from a PDF."""
        try:
            # Get PDF metadata
            metadata = await self.pdf_repository.get_pdf_metadata(pdf_id)
            if not metadata:
                self.logger.error(f"PDF metadata not found for ID: {pdf_id}")
                return False

            # Get PDF file content
            file_content = await self.pdf_repository.get_pdf_file(metadata.file_id)
            if not file_content:
                self.logger.error(f"PDF file content not found for file_id: {metadata.file_id}")
                return False

            # Parse PDF content
            pdf_file = io.BytesIO(file_content)
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                if not pdf_reader.pages:
                    self.logger.error("PDF has no pages")
                    return False

                text_content = ""
                for i, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                        else:
                            self.logger.warning(f"No text extracted from page {i+1}")
                    except Exception as page_error:
                        self.logger.error(f"Error extracting text from page {i+1}: {str(page_error)}")
                        continue

                if not text_content.strip():
                    self.logger.error("No text content extracted from PDF")
                    return False

                # Update metadata with parsed text
                success = await self.pdf_repository.update_pdf_text(pdf_id, text_content)
                if not success:
                    self.logger.error("Failed to update PDF text content in database")
                    return False

                return True

            except PyPDF2.PdfReadError as pdf_error:
                self.logger.error(f"PDF read error: {str(pdf_error)}")
                return False
            except Exception as pdf_error:
                self.logger.error(f"Error processing PDF: {str(pdf_error)}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to parse PDF: {str(e)}")
            return False

    async def select_pdf(self, pdf_id: str, user_id: int) -> Optional[PDFMetadata]:
        """Select a PDF for chat."""
        metadata = await self.pdf_repository.get_pdf_metadata(pdf_id)
        if not metadata:
            return None

        # Check if PDF is parsed
        if not metadata.parsed:
            success = await self.parse_pdf(pdf_id)
            if not success:
                return None
            # Get updated metadata
            metadata = await self.pdf_repository.get_pdf_metadata(pdf_id)

        # Store selected PDF in MongoDB
        success = await self.pdf_repository.set_selected_pdf(user_id, pdf_id)
        if not success:
            self.logger.error(f"Failed to store selected PDF for user {user_id}")
            return None

        return metadata

    async def get_selected_pdf(self, user_id: int) -> Optional[PDFMetadata]:
        """Get currently selected PDF for a specific user."""
        pdf_id = await self.pdf_repository.get_selected_pdf(user_id)
        if not pdf_id:
            return None
        return await self.pdf_repository.get_pdf_metadata(pdf_id)

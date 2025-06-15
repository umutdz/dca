import io
from typing import List, Optional

import PyPDF2
from fastapi import UploadFile

from app.middleware.logging import default_logger
from app.repositories.mongodb.pdf import PDFMetadata, PDFRepository


class PDFService:
    def __init__(self):
        self.pdf_repository = PDFRepository()

    async def upload_pdf(self, title: str, filename: str, file: UploadFile, user_id: int) -> PDFMetadata:
        """Upload a PDF file to MongoDB GridFS and store its metadata."""
        try:
            # Read file content
            file_content = await file.read()

            # Upload to MongoDB
            metadata = await self.pdf_repository.upload_pdf(user_id=user_id, filename=filename, title=title, file_content=file_content)

            default_logger.info("PDF uploaded successfully", user_id=user_id, filename=filename, title=title, pdf_id=metadata.id)

            return metadata
        except Exception as e:
            default_logger.error("Failed to upload PDF", user_id=user_id, filename=filename, title=title, error=str(e))
            raise

    async def get_user_pdfs(self, user_id: int) -> List[PDFMetadata]:
        """Get all PDFs uploaded by a specific user."""
        try:
            pdfs = await self.pdf_repository.get_user_pdfs(user_id)
            default_logger.info("Retrieved user PDFs", user_id=user_id, pdf_count=len(pdfs))
            return pdfs
        except Exception as e:
            default_logger.error("Failed to get user PDFs", user_id=user_id, error=str(e))
            raise

    async def parse_pdf(self, pdf_id: str) -> bool:
        """Extract and save text content from a PDF."""
        try:
            # Get PDF metadata
            metadata = await self.pdf_repository.get_pdf_metadata(pdf_id)
            if not metadata:
                default_logger.error("PDF metadata not found", pdf_id=pdf_id)
                return False

            # Get PDF file content
            file_content = await self.pdf_repository.get_pdf_file(metadata.file_id)
            if not file_content:
                default_logger.error("PDF file content not found", pdf_id=pdf_id, file_id=metadata.file_id)
                return False

            # Parse PDF content
            pdf_file = io.BytesIO(file_content)
            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                if not pdf_reader.pages:
                    default_logger.error("PDF has no pages", pdf_id=pdf_id)
                    return False

                text_content = ""
                for i, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += page_text + "\n"
                        else:
                            default_logger.warning("No text extracted from page", pdf_id=pdf_id, page_number=i + 1)
                    except Exception as page_error:
                        default_logger.error("Error extracting text from page", pdf_id=pdf_id, page_number=i + 1, error=str(page_error))
                        continue

                if not text_content.strip():
                    default_logger.error("No text content extracted from PDF", pdf_id=pdf_id)
                    return False

                # Update metadata with parsed text
                success = await self.pdf_repository.update_pdf_text(pdf_id, text_content)
                if not success:
                    default_logger.error("Failed to update PDF text content in database", pdf_id=pdf_id)
                    return False

                default_logger.info("PDF parsed successfully", pdf_id=pdf_id, page_count=len(pdf_reader.pages))
                return True

            except PyPDF2.PdfReadError as pdf_error:
                default_logger.error("PDF read error", pdf_id=pdf_id, error=str(pdf_error))
                return False
            except Exception as pdf_error:
                default_logger.error("Error processing PDF", pdf_id=pdf_id, error=str(pdf_error))
                return False

        except Exception as e:
            default_logger.error("Failed to parse PDF", pdf_id=pdf_id, error=str(e))
            return False

    async def select_pdf(self, pdf_id: str, user_id: int) -> Optional[PDFMetadata]:
        """Select a PDF for chat."""
        metadata = await self.pdf_repository.get_pdf_metadata(pdf_id)
        if not metadata:
            default_logger.warning("PDF not found for selection", pdf_id=pdf_id, user_id=user_id)
            return None

        # Check if PDF is parsed
        if not metadata.parsed:
            success = await self.parse_pdf(pdf_id)
            if not success:
                default_logger.error("Failed to parse PDF during selection", pdf_id=pdf_id, user_id=user_id)
                return None
            # Get updated metadata
            metadata = await self.pdf_repository.get_pdf_metadata(pdf_id)

        # Store selected PDF in MongoDB
        success = await self.pdf_repository.set_selected_pdf(user_id, pdf_id)
        if not success:
            default_logger.error("Failed to store selected PDF", pdf_id=pdf_id, user_id=user_id)
            return None

        default_logger.info("PDF selected successfully", pdf_id=pdf_id, user_id=user_id)
        return metadata

    async def get_selected_pdf(self, user_id: int) -> Optional[PDFMetadata]:
        """Get currently selected PDF for a specific user."""
        pdf_id = await self.pdf_repository.get_selected_pdf(user_id)
        if not pdf_id:
            default_logger.info("No PDF selected for user", user_id=user_id)
            return None

        metadata = await self.pdf_repository.get_pdf_metadata(pdf_id)
        if metadata:
            default_logger.info("Retrieved selected PDF", user_id=user_id, pdf_id=pdf_id)
        return metadata

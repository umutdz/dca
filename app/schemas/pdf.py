from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PDFUploadRequest(BaseModel):
    """Request model for PDF upload."""

    title: str = Field(..., description="The title of the PDF file")
    filename: str = Field(..., description="The name of the PDF file")


class PDFMetadata(BaseModel):
    """Base PDF metadata model."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="The unique identifier of the PDF")
    user_id: int = Field(..., description="The ID of the user who uploaded the PDF")
    title: str = Field(..., description="The title of the PDF file")
    filename: str = Field(..., description="The name of the PDF file")
    upload_date: datetime = Field(..., description="The upload date of the PDF file")
    file_id: str = Field(..., description="The file identifier")
    parsed: bool = Field(default=False, description="Whether the PDF has been parsed")
    text_content: Optional[str] = Field(None, description="The extracted text content of the PDF")


class PDFListResponse(BaseModel):
    """Response model for PDF list."""

    model_config = ConfigDict(from_attributes=True)

    pdfs: List[PDFMetadata] = Field(..., description="List of PDFs")


class PDFParseResponse(BaseModel):
    """Response model for PDF parse."""

    message: str = Field(..., description="Status message")
    pdf_id: str = Field(..., description="The ID of the parsed PDF")


class PDFSelectResponse(BaseModel):
    """Response model for PDF selection."""

    message: str = Field(..., description="Status message")
    pdf: PDFMetadata = Field(..., description="The selected PDF metadata")


class PDFChatResponse(BaseModel):
    """Response model for PDF chat."""

    model_config = ConfigDict(from_attributes=True)

    question: str = Field(..., description="The question")
    answer: str = Field(..., description="The answer")
    pdf_id: str = Field(..., description="The ID of the PDF")


class PDFChatRequest(BaseModel):
    """Request model for PDF chat."""

    question: str = Field(..., description="The question")


class PDFChatHistoryResponse(BaseModel):
    """Response model for PDF chat history."""

    model_config = ConfigDict(from_attributes=True)

    history: List[Dict[str, Any]] = Field(..., description="List of chat history items")

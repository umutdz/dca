from typing import Dict, List

from pydantic import Field

from app.schemas.base import BaseAPISerializer


class GeminiChatRequest(BaseAPISerializer):
    """Request model for Gemini chat."""

    contents: List[Dict[str, List[Dict[str, str]]]] = Field(
        ..., description="The contents to send to the model", example=[{"parts": [{"text": "What is this document about?"}]}]
    )


class GeminiChatResponse(BaseAPISerializer):
    """Response model for Gemini chat."""

    question: str = Field(..., description="The response from the model")
    answer: str = Field(..., description="The response from the model")
    pdf_id: str = Field(..., description="The response from the model")

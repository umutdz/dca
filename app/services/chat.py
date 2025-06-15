import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.repositories.mongodb.pdf import PDFMetadata
from app.repositories.postgres.chat import PostgreChatHistoryRepository
from app.schemas.api import GeminiChatRequest, GeminiChatResponse
from app.schemas.pdf import PDFChatHistoryResponse
from app.services.api import APIService


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_service = APIService(
            base_url=config.GEMINI_BASE_URL,
        )

    async def chat_pdf(self, question: str, pdf: PDFMetadata, user_id: str) -> GeminiChatResponse:
        # TODO: add log
        prompt = f"""
        You are a helpful assistant that can answer questions about the following PDF:
        {pdf.text_content}
        User: {question}
        Assistant:
        """
        request = GeminiChatRequest(contents=[{"parts": [{"text": prompt}]}])
        response = self.api_service._make_request(
            method="POST",
            endpoint=f"{config.GEMINI_ENDPOINT}?key={config.GEMINI_API_KEY}",
            data=request,
        )

        # Extract the answer from Gemini response
        answer = response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        await PostgreChatHistoryRepository(self.db).create(
            {"user_id": int(user_id), "question": question, "answer": answer, "session_id": str(uuid.uuid4())}
        )
        return GeminiChatResponse(question=question, answer=answer, pdf_id=pdf.id)

    async def chat_history(self, user_id: str) -> PDFChatHistoryResponse:
        history = await PostgreChatHistoryRepository(self.db).get_chat_history(user_id)
        formatted_history = [
            {"user_id": item.user_id, "question": item.question, "answer": item.answer, "session_id": item.session_id} for item in history
        ]
        return PDFChatHistoryResponse(history=formatted_history)

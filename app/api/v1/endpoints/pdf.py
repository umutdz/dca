from fastapi import APIRouter, Depends, File, Header, UploadFile

from app.api.deps import depends_pdf_service, get_current_user
from app.core.error_codes import ErrorCode
from app.core.exceptions import ExceptionBase
from app.schemas.pdf import (PDFListResponse, PDFMetadata, PDFParseResponse,
                             PDFSelectResponse)
from app.services.pdf import PDFService

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("/upload", response_model=PDFMetadata)
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = None,
    filename: str = None,
    authorization: str = Header(..., description="Bearer token"),
    service: PDFService = Depends(depends_pdf_service),
):
    """
    Upload a PDF file to MongoDB using GridFS.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise ExceptionBase(ErrorCode.INVALID_FILE_TYPE)

    user = await get_current_user(authorization)
    try:
        return await service.upload_pdf(title=title or file.filename, filename=filename or file.filename, file=file, user_id=user.id)
    except Exception:
        raise ExceptionBase(ErrorCode.PDF_UPLOAD_FAILED)


@router.get("/list", response_model=PDFListResponse)
async def list_pdfs(authorization: str = Header(..., description="Bearer token"), service: PDFService = Depends(depends_pdf_service)):
    """
    Get list of all PDFs uploaded by the authenticated user.
    """
    user = await get_current_user(authorization)
    try:
        pdfs = await service.get_user_pdfs(user.id)
        return PDFListResponse(pdfs=pdfs)
    except Exception:
        raise ExceptionBase(ErrorCode.DATABASE_ERROR)


@router.post("/parse/{pdf_id}", response_model=PDFParseResponse)
async def parse_pdf(
    pdf_id: str, authorization: str = Header(..., description="Bearer token"), service: PDFService = Depends(depends_pdf_service)
):
    """
    Extract and save text content from a selected PDF.
    This must be done before using the chat feature.
    """
    user = await get_current_user(authorization)

    # Get PDF metadata to check ownership
    pdfs = await service.get_user_pdfs(user.id)
    if not any(pdf.id == pdf_id for pdf in pdfs):
        raise ExceptionBase(ErrorCode.PDF_ACCESS_DENIED)

    # Check if PDF is already parsed
    pdf = next((p for p in pdfs if p.id == pdf_id), None)
    if pdf and pdf.parsed:
        raise ExceptionBase(ErrorCode.PDF_ALREADY_PARSED)

    try:
        success = await service.parse_pdf(pdf_id)
        if not success:
            raise ExceptionBase(ErrorCode.PDF_PARSE_FAILED)

        return PDFParseResponse(message="PDF parsed successfully", pdf_id=pdf_id)
    except Exception:
        raise ExceptionBase(ErrorCode.PDF_PARSE_FAILED)


@router.post("/select/{pdf_id}", response_model=PDFSelectResponse)
async def select_pdf(
    pdf_id: str, authorization: str = Header(..., description="Bearer token"), service: PDFService = Depends(depends_pdf_service)
):
    """
    Select a previously uploaded PDF to chat with.
    The PDF will be automatically parsed if it hasn't been parsed before.
    """
    user = await get_current_user(authorization)

    # Get PDF metadata to check ownership
    pdfs = await service.get_user_pdfs(user.id)
    if not any(pdf.id == pdf_id for pdf in pdfs):
        raise ExceptionBase(ErrorCode.PDF_ACCESS_DENIED)

    try:
        selected_pdf = await service.select_pdf(pdf_id)
        if not selected_pdf:
            raise ExceptionBase(ErrorCode.PDF_SELECTION_FAILED)

        return PDFSelectResponse(message="PDF selected successfully", pdf=selected_pdf)
    except Exception:
        raise ExceptionBase(ErrorCode.PDF_SELECTION_FAILED)

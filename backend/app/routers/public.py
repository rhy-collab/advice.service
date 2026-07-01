from fastapi import APIRouter, File, UploadFile

from app.schemas.public import ContractCheckResponse, PublicIntakeRequest, PublicIntakeResponse
from app.services.document_checker import MAX_CHECK_BYTES, document_checker
from app.services.intake_service import intake_service

router = APIRouter(prefix="/public", tags=["public"])


@router.post("/check-contract", response_model=ContractCheckResponse)
async def check_contract(file: UploadFile = File(...)) -> ContractCheckResponse:
    content = await read_limited_upload(file)
    return document_checker.check_docx(file.filename or "contract.docx", content)


@router.post("/intake", response_model=PublicIntakeResponse)
def create_public_intake(request: PublicIntakeRequest) -> PublicIntakeResponse:
    return intake_service.create_public_intake(request)


async def read_limited_upload(file: UploadFile) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_CHECK_BYTES:
            from fastapi import HTTPException

            raise HTTPException(status_code=413, detail="Document is too large for the free checker")
        chunks.append(chunk)
    return b"".join(chunks)

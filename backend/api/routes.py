from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ingestion import ingest_file

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        result = await ingest_file(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class SummaryRequest(BaseModel):
    query: str

@router.post("/summarize")
async def summarize(request: SummaryRequest):
    from services.summarization import generate_summary
    try:
        summary = await generate_summary(request.query)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

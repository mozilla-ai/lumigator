from fastapi import APIRouter

from src.schemas.extras import  Status

router = APIRouter()

@router.get("/status")
async def get_status() -> Status:
    endpoint_results = {
    "id": "ABC123",
    "model": "hf/modelname",
    "Status": "PENDING",
    }

    return Status(endpoint_results)

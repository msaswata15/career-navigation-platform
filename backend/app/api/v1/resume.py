from fastapi import APIRouter

router = APIRouter()

@router.post("/upload")
async def upload_resume():
    pass

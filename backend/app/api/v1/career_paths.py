from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_career_paths():
    pass

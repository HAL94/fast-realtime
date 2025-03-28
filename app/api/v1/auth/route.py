from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login():
    return {"todo": "not yet implemented"}

from fastapi import APIRouter

from .auth.route import router as auth_router
from .games.route import router as games_router


router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(games_router)
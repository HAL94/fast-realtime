from app.core.config import AppSettings
from app.core.setup import create_application
from app.api import router as api_router
from app.websocket import router as ws_router
from app.utils.leaderboard import generate_leaderboard_data

app = create_application(
    api_router=api_router, ws_router=ws_router, settings=AppSettings()
)


leaderboard = []
@app.post("/")
async def generate_leaderboard():
    global leaderboard
    leaderboard = generate_leaderboard_data()
    return {"success": True}
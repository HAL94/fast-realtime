import random
from datetime import datetime, timedelta

from app.core.db.models import User

def generate_leaderboard_data(players: list[User]):
    """Generates random leaderboard data."""

    games = ["Call of Duty", "Valorant", "Minecraft", "Fortnite", "Apex Legends", "League of Legends", "Overwatch", "Counter-Strike", "Rocket League", "PUBG"]    
    leaderboard = []

    for rank, player in enumerate(players):
        game = random.choice(games)
        score = random.randint(100, 1000)
        date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d') # Random dates within the last 30 days.

        entry = {
            "rank": rank,
            "id": player.id,
            "player": player.name,
            "game": game,
            "score": score,
            "date": date
        }
        
        leaderboard.append(entry)

    return leaderboard
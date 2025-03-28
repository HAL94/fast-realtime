import random
from datetime import datetime, timedelta

def generate_leaderboard_data(num_entries=10):
    """Generates random leaderboard data."""

    games = ["Call of Duty", "Valorant", "Minecraft", "Fortnite", "Apex Legends", "League of Legends", "Overwatch", "Counter-Strike", "Rocket League", "PUBG"]
    players = [f"Player_{i}" for i in range(1, 101)] # Generate 100 player names
    leaderboard = []

    for rank in range(1, num_entries + 1):
        player = random.choice(players)
        game = random.choice(games)
        score = random.randint(100, 1000)
        date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d') # Random dates within the last 30 days.

        entry = {
            "rank": rank,
            "player": player,
            "game": game,
            "score": score,
            "date": date
        }
        leaderboard.append(entry)

    return leaderboard
from app.redis.channels import ALL_GAMES, channels 
from app.seed.utils import clear_db, create_session_local, get_db
from .pg_seed import UserSeeder
from .redis_seed import ScoresSeeder


def seed_everything():
    clear_db()
    SessionLocal = create_session_local()
    db = next(get_db(SessionLocal=SessionLocal))
    user_seeder = UserSeeder()
    entries = 10

    user_data = user_seeder.seed(num_entries=entries, db=db)

    selected_channels = [key for key in channels if key != ALL_GAMES]
    seeders = [ScoresSeeder(data=user_data, channel=channel) for channel in selected_channels]
    
    for game_seeder in seeders:
        game_seeder.seed()
    
    
    


if __name__ == "__main__":
    seed_everything()

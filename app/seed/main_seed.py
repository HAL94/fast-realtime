from app.seed.utils import create_session_local, get_db
from .pg_seed import UserSeeder
from .redis_seed import ScoresSeeder


def seed_everything():
    SessionLocal = create_session_local()
    db = next(get_db(SessionLocal=SessionLocal))
    user_seeder = UserSeeder()
    entries = 10

    user_data = user_seeder.seed(num_entries=entries, db=db)
    scores_seeder = ScoresSeeder(data=user_data)
    scores_seeder.seed()


if __name__ == "__main__":
    seed_everything()

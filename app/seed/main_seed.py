from app.redis.channels import COD, FORTNITE
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

    # dependend on previous seeder
    cod_scores_seeder = ScoresSeeder(data=user_data, channel=COD)
    cod_scores_seeder.seed()
    
    fortnite_scores_seeder = ScoresSeeder(data=user_data, channel=FORTNITE)
    fortnite_scores_seeder.seed()


if __name__ == "__main__":
    seed_everything()

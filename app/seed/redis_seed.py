import redis
from app.core.db.models import User
from app.seed.base import SeederBase
from app.seed.utils import create_redis_client
from .leaderboard import generate_leaderboard_data


class ScoresSeeder(SeederBase):
    name = "Score Seeder"
    channel = "scores"

    def __init__(self, data):
        super().__init__(data=data)
        self.client = create_redis_client()
        self.data = self._transform(data)

    def _transform(self, data):
        leaderboard_data = clear_and_recreate_scores(
            players=data,
            redis_client=self.client,
            sorted_set_name=self.channel,
        )
        self._transformed = leaderboard_data        
        transform_leaderboard_data = [
            (entry.get("score"), entry.get("id")) for entry in leaderboard_data
        ]
        print(f"redis data: {transform_leaderboard_data}")
        return transform_leaderboard_data

    def seed(self):
        for (id, score), player_info in zip(self.data, self._transformed):
            self.client.zadd(self.channel, {score: id})
            self.client.hset(name=f"{player_info.get("id")}", mapping=player_info)


def clear_and_recreate_scores(players: list[User], redis_client, sorted_set_name):
    """
    Clears an existing Redis sorted set and recreates it.

    Args:
        redis_client: A Redis client instance.
        sorted_set_name: The name of the sorted set.
    """
    try:
        # Check if the sorted set exists
        if redis_client.exists(sorted_set_name):
            # Delete the existing sorted set
            redis_client.delete(sorted_set_name)
            print(f"Sorted set '{sorted_set_name}' deleted.")
        else:
            print(f"Sorted set '{sorted_set_name}' does not exist, creating it.")

        # Create the sorted set (even if it was just deleted)
        # You can add initial values here if needed.
        # For an empty set, you don't need to add anything.
        print(f"Sorted set '{sorted_set_name}' recreated.")

        leaderboard = generate_leaderboard_data(players)

        print(f"successfully got a sample leaderboard: {leaderboard}")

        return leaderboard

    except redis.exceptions.RedisError as e:
        print(f"Redis error: {e}")


def main():
    """
    Main function to connect to Redis and clear/recreate the sorted set.
    """
    try:
        # Replace with your Redis connection details
        redis_host = "localhost"
        redis_port = 6379
        redis_db = 0
        redis_password = None  # If you have a password, fill it in

        redis_client = redis.Redis(
            host=redis_host, port=redis_port, db=redis_db, password=redis_password
        )
        redis_client.ping()  # Check if the connection is successful
        print("Redis connection successful.")

        sorted_set_name = "scores"  # Replace with your sorted set name
        clear_and_recreate_scores(redis_client, sorted_set_name)

    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

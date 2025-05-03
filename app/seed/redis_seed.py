import redis
from app.redis.channels import ALL_GAMES
from app.seed.base import SeederBase
from app.seed.utils import create_redis_client
from .utils import generate_leaderboard_data


class ScoresSeeder(SeederBase):
    name = "Score Seeder"

    def __init__(self, data, channel):
        super().__init__(data=data)
        self.client = create_redis_client()
        self.channel = channel
        self._transformed = self._transform()

    def _transform(
        self,
    ):
        clear_and_recreate_sortedset(
            redis_client=self.client,
            sorted_set_name=self.channel,
        )
        leaderboard_data = generate_leaderboard_data(self.data, self.channel)
        return leaderboard_data

    def seed(self):
        for entry in self._transformed:
            user_id = entry.user_id
            score = entry.score
            player_info = entry.model_dump()
            key = f"{user_id}:{self.channel}"

            self.client.zadd(self.channel, {key: score})
            self.client.hset(name=key, mapping=player_info)
            
            dt_suffix = entry.date
            dt_key = f"{key}:{dt_suffix}"
            
            key = f"{ALL_GAMES}:{user_id}:{self.channel}"
            self.client.zadd(ALL_GAMES, mapping={key: score})
            self.client.hset(name=key, mapping=player_info)
            self.client.hset(name=dt_key, mapping=player_info)
            
            channel_by_date = f"lb:{entry.date}"
            self.client.zadd(channel_by_date, {dt_key: score})


def clear_and_recreate_sortedset(redis_client: redis.Redis, sorted_set_name: str):
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

        clear_and_recreate_sortedset(redis_client, ALL_GAMES)

    except redis.exceptions.ConnectionError as e:
        print(f"Failed to connect to Redis: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

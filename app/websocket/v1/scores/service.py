from datetime import datetime
from fastapi import Depends

from app.core.auth.schema import UserRead
from app.websocket.v1.scores.schema import PlayerRank, SubmitScore
from .repository import ScoresRepository, get_scores_repo
from app.redis.channels import ALL_GAMES, channels_dict


class ScoreService:
    def __init__(self, scores_repo: ScoresRepository):
        self.scores_repo = scores_repo

    async def get_leaderboard_data(self, game_channel: str) -> list[dict]:
        data = await self.scores_repo.zrevrange(
            key=game_channel, start=0, end=-1, withscores=True
        )

        if not data or not data.result:
            return []

        result = []

        for item in data.result:
            key = item.key

            leaderboard_data = await self.scores_repo.hgetall(name=key)

            leaderboard_data.game = channels_dict[leaderboard_data.game]

            if leaderboard_data:
                result.append(leaderboard_data.model_dump())

        return result

    async def get_top_user_score(self, user_id: int):
        keys = await self.scores_repo.get_keys_by_pattern(
            pattern=f"{ALL_GAMES}:{user_id}:*"
        )

        top_user_rank = 9999
        top_rank_key = None
        result = None

        for key in keys:
            rank = await self.scores_repo.zrevrank(sorted_set_name=ALL_GAMES, key=key)
            if rank < top_user_rank:
                top_user_rank = rank
                top_rank_key = key

        result: PlayerRank = await self.scores_repo.hgetall(name=top_rank_key)

        result.rank = top_user_rank + 1  # ranking is 0-based
        result.game = channels_dict[result.game]

        return result

    async def add_user_score(self, data: SubmitScore, user_data: UserRead):
        game_channel = data.game_channel
        score = data.score

        if game_channel not in channels_dict:
            return None

        key = f"{user_data.id}:{game_channel}"

        entry = {
            "rank": -1,
            "id": user_data.id,
            "player": user_data.name,
            "game": game_channel,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }

        await self.scores_repo.client.zadd(game_channel, {key: score})
        await self.scores_repo.client.hset(name=key, mapping=entry)

        key = f"{ALL_GAMES}:{user_data.id}:{game_channel}"
        await self.scores_repo.client.zadd(ALL_GAMES, mapping={key: score})
        await self.scores_repo.client.hset(name=key, mapping=entry)


async def get_score_service(scores_repo: ScoresRepository = Depends(get_scores_repo)):
    return ScoreService(scores_repo)

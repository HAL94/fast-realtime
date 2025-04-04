from fastapi import Depends
from app.redis.channels import SCORES_CHANNEL
from .repository import ScoresRepository, get_scores_repo


class ScoreService:
    def __init__(self, scores_repo: ScoresRepository):
        self.scores_repo = scores_repo

    async def get_leaderboard_data(self) -> list[dict]:
        data = await self.scores_repo.zrevrange(
            key=SCORES_CHANNEL, start=0, end=-1, withscores=True
        )

        if not data or not data.result:
            return []

        result = []
        for item in data.result:
            leaderboard_data = await self.scores_repo.hgetall(name=item.key)

            if leaderboard_data:
                result.append(leaderboard_data.model_dump())

        return result


async def get_score_service(scores_repo: ScoresRepository = Depends(get_scores_repo)):
    return ScoreService(scores_repo)

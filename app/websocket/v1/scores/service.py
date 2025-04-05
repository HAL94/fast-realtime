from fastapi import Depends
from app.redis.channels import ALL_GAMES
from .repository import ScoresRepository, get_scores_repo


class ScoreService:
    def __init__(self, scores_repo: ScoresRepository):
        self.scores_repo = scores_repo

    async def get_all_leaderboard_data(self,):
        data = await self.scores_repo.zrevrange(
            key=ALL_GAMES, start=0, end=-1, withscores=True
        )
        
        if not data or not data.result:
            return []
        
        result = []        
        
        for item in data.result:
            
            key = item.key
            keys = key.split(":")[1:]
            id, channel = keys[0], keys[1]
            
            score_data = await self.scores_repo.hgetall(name=f"{id}:{channel}")
            # print("score_data", score_data)
            if score_data:
                result.append(score_data.model_dump())
        
        return result
            
            
            
        
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
            
            if leaderboard_data:
                result.append(leaderboard_data.model_dump())

        return result


async def get_score_service(scores_repo: ScoresRepository = Depends(get_scores_repo)):
    return ScoreService(scores_repo)

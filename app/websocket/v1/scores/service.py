from fastapi import Depends
from .repository import ScoresRepository, get_scores_repo
from app.redis.channels import channels_dict


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
            
            if leaderboard_data:
                result.append(leaderboard_data.model_dump())

        return result

    async def get_user_score_by_game(self, game_channel: str, user_id: int):
        if game_channel not in channels_dict:
            return None
        
        
        key = f"{user_id}:{game_channel}"
                
        user_score_data = await self.scores_repo.hgetall(name=key)
                
        return user_score_data


async def get_score_service(scores_repo: ScoresRepository = Depends(get_scores_repo)):
    return ScoreService(scores_repo)

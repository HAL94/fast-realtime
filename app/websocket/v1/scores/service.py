import datetime
from typing import Optional
from fastapi import Depends

from app.core.auth.schema import UserRead

from app.websocket.v1.scores.schema import (
    GetReportRequest,
    PlayerRank,
    PlayerRankAdd,    
    ReportItem,
    ReportResponse,
    SubmitScore,
)
from .repository import ScoresRepository, get_scores_repo
from app.redis.channels import ALL_GAMES, channels_dict


class ScoreService:
    def __init__(self, scores_repo: ScoresRepository):
        self.scores_repo = scores_repo

    async def get_leaderboard_count(self, game_channel: str = ALL_GAMES):
        data = await self.scores_repo.zrevrange(key=game_channel, start=0, end=-1)

        total_count = len(data.result)

        return total_count

    async def get_leaderboard_data(
        self, game_channel: str, start: Optional[int] = 0, end: Optional[int] = -1
    ) -> list[dict]:
        data = await self.scores_repo.zrevrange(
            key=game_channel, start=start, end=end, withscores=True
        )

        if not data or not data.result:
            return []

        result = []

        for item in data.result:
            key = item.key

            leaderboard_data = await self.scores_repo.hgetall(name=key)
            leaderboard_data.game = channels_dict[leaderboard_data.game]
            rank = await self.scores_repo.zrevrank(
                sorted_set_name=game_channel, key=key
            )
            leaderboard_data.rank = rank + 1

            if leaderboard_data:
                result.append(leaderboard_data.model_dump())

        data = await self.scores_repo.zrevrange(key=game_channel, start=0, end=-1)

        total_count = len(data.result)

        return result, total_count

    async def _get_player_games(self, user_id: int):
        keys = await self.scores_repo.get_keys_by_pattern(
            pattern=f"{ALL_GAMES}:{user_id}:*"
        )

        return keys

    async def get_top_user_score(self, user_id: int):
        keys = await self._get_player_games(user_id)
        top_user_rank = float("inf")
        top_rank_key = None
        result = None

        for key in keys:
            rank = await self.scores_repo.zrevrank(sorted_set_name=ALL_GAMES, key=key)
            if rank < top_user_rank:
                top_user_rank = rank
                top_rank_key = key

        if not top_rank_key:
            return None

        result: PlayerRank = await self.scores_repo.hgetall(name=top_rank_key)

        result.rank = top_user_rank + 1  # ranking is 0-based
        result.game = channels_dict[result.game]

        return result

    async def add_user_score(self, data: SubmitScore, user_data: UserRead):
        PREFIX = "lb"
        game_channel = data.game_channel
        score = data.score

        if game_channel not in channels_dict:
            return None

        key = f"{user_data.id}:{game_channel}"

        date = datetime.datetime.now()

        entry = PlayerRankAdd(
            user_id=user_data.id,
            player=user_data.name,
            game=game_channel,
            score=score,
            date=date.strftime("%Y-%m-%d"),
        )

        await self.scores_repo.client.zadd(game_channel, {key: score})
        # update current record with new date or create new
        await self.scores_repo.client.hset(name=key, mapping=entry.model_dump())

        # store a separate key-value pair for the current date
        dt_suffix = date.strftime("%Y-%m-%d")
        # extend current key with date suffix. E.g: 1:cod:2025-05-03
        dt_key = f"{key}:{dt_suffix}"
        await self.scores_repo.client.hset(name=dt_key, mapping=entry.model_dump())

        key = f"{ALL_GAMES}:{user_data.id}:{game_channel}"
        await self.scores_repo.client.zadd(ALL_GAMES, mapping={key: score})
        await self.scores_repo.client.hset(name=key, mapping=entry.model_dump())

        # keep a sorted set for this particular date.
        # Any players who submitted in this date, can have date-specific leaderboard.
        channel_by_date = f"{PREFIX}:{dt_suffix}"
        await self.scores_repo.client.zadd(channel_by_date, {dt_key: score})

    async def get_reports(self, data: GetReportRequest) -> ReportResponse:
        start_date = data.start
        end_date = data.end

        delta = datetime.timedelta(days=1)
        PREFIX = "lb"

        timestamp_keys = []

        while start_date <= end_date:
            date_key = start_date.strftime("%Y-%m-%d")
            start_date += delta
            timestamp_keys.append(f"{PREFIX}:{date_key}")

        top_data = await self.scores_repo.zunionstore(
            keys=timestamp_keys, end=data.limit - 1, withscores=True
        )

        if not top_data:
            return []

        result: list[ReportItem] = []

        for rank, item in enumerate(top_data.result):
            key = item.key
            leaderboard_item = await self.scores_repo.hgetall(name=key)
            leaderboard_item.rank = rank + 1
            leaderboard_item.score = item.score

            user_id = key.split(":")[0]
            
            player_games = await self._get_player_games(user_id)
            
            report_item = ReportItem(
                name=leaderboard_item.player,
                score=leaderboard_item.score,
                games=len(player_games),
                game=channels_dict[leaderboard_item.game],
                date=leaderboard_item.date,
            )

            result.append(report_item.model_dump())
        

        return ReportResponse(result=result)


async def get_score_service(scores_repo: ScoresRepository = Depends(get_scores_repo)):
    return ScoreService(scores_repo)

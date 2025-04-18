
from app.api.v1.games.schema import GameChannel
from app.redis.channels import channels_dict

def get_game_channels():
    return [GameChannel(label=v, value=k) for k, v in channels_dict.items()]
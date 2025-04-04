from typing import Final


ALL_GAMES: Final[str] = "all"
COD: Final[str] = "call_of_duty"
VALORANT: Final[str] = "valorant"
MINECRAFT: Final[str] = "minecraft"
FORTNITE: Final[str] = "fortnite"
APEX_LEGENGS: Final[str] = "apex_legends"
LEAGUE_OF_LEGENDS: Final[str] = "league_of_legends"
OVERWATCH: Final[str] = "overwatch"
CS: Final[str] = "counter_strike"
ROCKET_LEAGUE: Final[str] = "rocket_league"
PUBG: Final[str] = "pubg"

channels_dict = {
    ALL_GAMES: "All",
    COD: "Call of Duty",
    VALORANT: "Valorant",
    MINECRAFT: "Minecraft",
    FORTNITE: "Fortnite",
    APEX_LEGENGS: "Apex Legends",
    LEAGUE_OF_LEGENDS: "League of Legends",
    OVERWATCH: "Overwatch",
    CS: "Counter Strike",
    ROCKET_LEAGUE: "Rocket League",
    PUBG: "PUBG",
}

channels = channels_dict.keys()
channel_labels = channels_dict.values()

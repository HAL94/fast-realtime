from typing import Final


ALL_GAMES: Final[str] = "all"
COD: Final[str] = "cod"
VALORANT: Final[str] = "valrnt"
MINECRAFT: Final[str] = "mcft"
FORTNITE: Final[str] = "fnite"
APEX_LEGENGS: Final[str] = "apxleg"
LEAGUE_OF_LEGENDS: Final[str] = "lol"
OVERWATCH: Final[str] = "ow"
CS: Final[str] = "cs"
ROCKET_LEAGUE: Final[str] = "rl"
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

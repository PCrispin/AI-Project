from enum import Enum


class block_codes(Enum):
    """Master list of all block codes that you want to interact
    with, or use

    Args:
        Enum (Int): Block code material
    """

    WATER = "minecraft:water"
    RED_WOOL = "red_wool"
    PURPLE_WOOL = "purple_wool"
    AIR = "air"

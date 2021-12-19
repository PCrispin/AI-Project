from enum import Enum


class block_codes(Enum):
    """Master list of all block codes

    Args:
        Enum (Int): Block code material
    """

    WATER = "minecraft:water"
    RED_WOOL = "red_wool"
    PURPLE_WOOL = "purple_wool"
    FLOWING_WATER = "minecraft:flowing_water"
    BUILDABLE = 2
    TREE = 3
    HOUSE = 7
    PROPOSED = 9
    FENCE = "minecraft:oak_fence"
    AIR = "minecraft:air"
    BEDROCK = "minecraft:bedrock"
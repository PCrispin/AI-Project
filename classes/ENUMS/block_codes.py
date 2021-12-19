from enum import Enum


class block_codes(Enum):
    """Master list of all block codes

    Args:
        Enum (Int): Block code material
    """

    WATER = "minecraft:water"
    FLOWING_WATER = "minecraft:flowing_water"
    ICE = "minecraft:ice"
    PACKED_ICE = "minecraft:packed_ice"
    BLUE_ICE = "minecraft:blue_ice"
    FROSTED_ICE = "minecraft:frosted_ice"

    RED_WOOL = "red_wool"
    PURPLE_WOOL = "purple_wool"
    BUILDABLE = 2
    TREE = 3
    HOUSE = 7
    PROPOSED = 9
    FENCE = "minecraft:oak_fence"
    AIR = "minecraft:air"
    BEDROCK = "minecraft:bedrock"
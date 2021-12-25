from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class block_codes(ExtendedEnum):
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
    FENCE = "minecraft:oak_fence"
    AIR = "minecraft:air"
    BEDROCK = "minecraft:bedrock"


class water_block_codes(ExtendedEnum):
    WATER = "minecraft:water"
    FLOWING_WATER = "minecraft:flowing_water"
    ICE = "minecraft:ice"
    PACKED_ICE = "minecraft:packed_ice"
    BLUE_ICE = "minecraft:blue_ice"
    FROSTED_ICE = "minecraft:frosted_ice"

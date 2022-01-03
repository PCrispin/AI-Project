"""Constants for the project"""

from classes.ENUMS.biome_ids import biome_regions
from classes.ENUMS.block_codes import block_codes


MAX_BUILDING_RADIUS = 13  # SHOULD BE ODD
MIN_BUILDING_RADIUS = 7
WATER_DISTANCE_WEIGHTING = 1.75
BUILDING_DISTANCE_WEIGHTING = 2
FLATNESS_FITNESS_WEIGHTING = 1
DEFAULT_MUTATION_RATE = 1 / 6
DEFAULT_POPULATION_SIZE = 5
GENERATIONS = 10
BUILDING_NUMBER = 12
POPULATION_SIZE = 40
AREA = (0, 0, 256, 256)  # x position, z position, x size, z size
WATER_SEARCH_RADIUS = (
    MAX_BUILDING_RADIUS * 2
)  # How far to search from building location for water, should be larger than MAX_BUILDING_RADIUS
MAXIMUM_WATER_DISTANCE_PENALTY = MAX_BUILDING_RADIUS
MAXIMUM_HOUSE_DISTANCE_PENALTY = AREA[2] + AREA[3]
IMAGE_DIR_FOLD = "data/images"

DEBUG_DRAW_WORKINGS: bool = False  # yellow/orange-first in frontier, light blue-candidate, NOT_POSSIBLE: Gray-drop or black
MAX_DETOUR: int = 110
VISITS_PER_BUILDING_TYPE = [
    0,  # building_types.HOUSE
    2,  # building_types.RESTAURANT
    5,  # building_types.FACTORY
    3,  # building_types.SHOP
    0,  # building_types.FLATS
    1,  # building_types.TOWN_HALL
]
BLOCK_BATCH_SIZE = 1000
WATER_CODES = [
    block_codes.WATER,
    block_codes.FLOWING_WATER,
    block_codes.ICE,
    block_codes.PACKED_ICE,
    block_codes.BLUE_ICE,
    block_codes.FROSTED_ICE,
]

RANDOM_SEED = 10


# Dictionary mapping biome ID to internal biome regional id
BIOME_MAP_DICTIONARY = dict(
    {
        4: 1,
        18: 1,
        27: 1,
        28: 1,
        29: 1,
        34: 1,
        132: 1,
        155: 1,
        156: 1,
        157: 1,
        179: 1,
        180: 1,
        1: 2,
        129: 2,
        2: 3,
        17: 3,
        130: 3,
        12: 4,
        13: 4,
        140: 4,
        26: 4,
        30: 4,
        31: 4,
        42: 4,
        45: 4,
        158: 4,
        35: 5,
        36: 5,
        163: 5,
        164: 5,
    }
)

# Dictionary mapping regions to variable block type
BIOME_BLOCK_MAP_DICTIONARY = dict(
    {
        biome_regions.FOREST: block_codes.DARK_OAK_WOOD,
        biome_regions.PLAINS: block_codes.DARK_OAK_WOOD,
        biome_regions.DESERT: block_codes.SANDSTONE,
        biome_regions.COLD: block_codes.EMERALD_ORE,
        biome_regions.SAVANNA: block_codes.BROWN_TERRACOTTA,
    }
)

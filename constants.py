"""Constants for the project"""

from classes.ENUMS.block_codes import block_codes


MAX_BUILDING_RADIUS = 13  # SHOULD BE ODD
MIN_BUILDING_RADIUS = 7
WATER_DISTANCE_WEIGHTING = 1.75
BUILDING_DISTANCE_WEIGHTING = 2
FLATNESS_FITNESS_WEIGHTING = 1
DEFAULT_MUTATION_RATE = 1 / 6
DEFAULT_POPULATION_SIZE = 5
GENERATIONS = 30
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

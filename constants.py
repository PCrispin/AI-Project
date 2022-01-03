"""Constants for the project"""

from typing import Tuple

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
VISITS_PER_BUILDING_TYPE: Tuple[int] = (
    0,  # building_types.HOUSE
    2,  # building_types.RESTAURANT
    5,  # building_types.FACTORY
    3,  # building_types.SHOP
    0,  # building_types.FLATS
    1,  # building_types.TOWN_HALL
)
BLOCK_BATCH_SIZE:int = 1000
MAX_HEIGHT:int = 255

GRID_WIDTH:int = 15
NUMBER_OF_FAMILIES_IN_A_FLAT:int = 5
DRIVE_LENGTH:int = 1
BUILDING_MARGIN:int = 3

RANDOM_SEED:int = 10

ENCOURAGE_PENALTY:float = 0.5
MAX_SNAP_TO_GRID_PENALTY:float = 2
NEAR_OBSTACLE_PENALTY:float = 1
THRESHOLD_GAIN_FOR_REENTRY_TO_FRONTIER: int = 2
LAMP_POST_SPACING:int = 10
ABORT_SEARCH_FOR_SITE_AFTER_ROUTE_NOT_FOUND_LIMIT:int = 4
MAX_HEIGHT_DROP:int = 1
MAX_DEPTH:int = 500
AREA_EXPANDED_MARGIN:int = 5

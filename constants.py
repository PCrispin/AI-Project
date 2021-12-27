"""Constants for the GA
    """

MAX_BUILDING_RADIUS = 11  # SHOULD BE ODD
MIN_BUILDING_RADIUS = 5
WATER_DISTANCE_WEIGHTING = 1.75
BUILDING_DISTANCE_WEIGHTING = 2
FLATNESS_FITNESS_WEIGHTING = 1
DEFAULT_MUTATION_RATE = 1 / 3
DEFAULT_POPULATION_SIZE = 5
GENERATIONS = 10
BUILDING_NUMBER = 5
POPULATION_SIZE = 20
AREA = (0, 0, 256, 256)  # x position, z position, x size, z size
WATER_SEARCH_RADIUS = (
    MAX_BUILDING_RADIUS * 8
)  # How far to search from building location for water, should be larger than MAX_BUILDING_RADIUS
MAXIMUM_DISTANCE_PENALTY = AREA[3] + AREA[2]
IMAGE_DIR_FOLD = "data/images"

DEBUG_DRAW_WORKINGS: bool = False  #yellow/orange-first in frontier, light blue-candidate, NOT_POSSIBLE: Gray-drop or black
MAX_DETOUR:int = 110
VISITS_PER_BUILDING_TYPE = [0, 2, 5, 3, 0, 1] #[HOUSE,RESTAURANT,FACTORY,SHOP,FLATS,TOWN_HALL]
BLOCK_BATCH_SIZE = 1000


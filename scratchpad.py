"""Attempting to create a flood fill search for water tiles
    """
from classes.Graph import manhattan
from classes.http_interface import get_world_state
from classes.misc_functions import get_build_coord
from constants import (
    AREA,
    MAX_BUILDING_RADIUS,
    MAXIMUM_DISTANCE_PENALTY,
    WATER_SEARCH_RADIUS,
)


# g_start = get_world_state(paint_fence=True, area=AREA)


check_vertexes = []
X = 256
Y = 256

# generate building indexes around it

water_tile_list = [(25, 25)]


def in_bounds(vector):
    (x_value, z_value) = vector
    if 0 <= x_value < X and 0 <= z_value < Y:
        return True
    else:
        return False


def calculate_water_distance_fitness(location):

    # If a location is IN water, return maximum distance
    build_locations = list(
        filter(in_bounds, get_build_coord(location=location, building_radius=3))
    )
    if any(x in build_locations for x in water_tile_list):
        print("Building in water")
        return MAXIMUM_DISTANCE_PENALTY

    start_vertex = (
        location[0] - int(WATER_SEARCH_RADIUS / 2),
        location[1] - int(WATER_SEARCH_RADIUS / 2),
    )

    end_vertex = (
        location[0] + int(WATER_SEARCH_RADIUS / 2),
        location[1] + int(WATER_SEARCH_RADIUS / 2),
    )

    # otherwise calculate if its near water

    for width in range(0, WATER_SEARCH_RADIUS):
        for height in range(0, WATER_SEARCH_RADIUS):
            check_vertexes.append((start_vertex[0] + width, start_vertex[1] + height))

    search_vertexs = list(filter(in_bounds, check_vertexes))

    if any(x in search_vertexs for x in water_tile_list):
        print("Water in search area")
        # get commonalities in both lists
        water_tiles_in_search_radius = list(
            set(search_vertexs).intersection(water_tile_list)
        )

        distances = {}
        for tile in water_tiles_in_search_radius:
            distances[tile] = manhattan(tile, location)
        closest_distance_vector = min(distances, key=distances.get)
        closest_distance_value = distances[closest_distance_vector]
        return closest_distance_value
    else:
        print("Water not in search area")
        return MAXIMUM_DISTANCE_PENALTY


test = calculate_water_distance_fitness((22, 22))
print(test)

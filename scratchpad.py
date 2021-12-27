"""Attempting to create a flood fill search for water tiles
    """

from classes.ENUMS.block_codes import block_codes
from classes.Graph import graph, manhattan
from classes.Tile import Tile
from classes.Timer import Timer
from classes.Types import GridLocation
from classes.http_interface import get_world_state, get_world_state_experimental
from classes.misc_functions import get_build_coord
from constants import (
    AREA,
    MAXIMUM_DISTANCE_PENALTY,
    WATER_SEARCH_RADIUS,
)
import random


search_tiles = []
for i in range(100):
    search_tiles.append((random.randint(1, 255), random.randint(1, 255)))


def in_bounds(vector):
    (x_value, z_value) = vector
    if 0 <= x_value < AREA[2] and 0 <= z_value < AREA[3]:
        return True
    else:
        return False


def flood_fill_search(location, g: graph):
    check_vertexes = []
    build_locations = list(
        filter(
            in_bounds,
            get_build_coord(location=location, building_radius=3),
        )
    )

    if any(x in build_locations for x in g.water_tiles):
        return MAXIMUM_DISTANCE_PENALTY

    start_vertex = (
        location[0] - int(WATER_SEARCH_RADIUS / 2),
        location[1] - int(WATER_SEARCH_RADIUS / 2),
    )

    for width in range(0, WATER_SEARCH_RADIUS):
        for height in range(0, WATER_SEARCH_RADIUS):
            check_vertexes.append((start_vertex[0] + width, start_vertex[1] + height))

    search_vertexs = list(filter(in_bounds, check_vertexes))

    if any(x in search_vertexs for x in g.water_tiles):
        water_tiles_in_search_radius = list(
            set(search_vertexs).intersection(g.water_tiles)
        )

        distances = {}
        for tile in water_tiles_in_search_radius:
            distances[tile] = manhattan(tile, location)
        closest_distance_vector = min(distances, key=distances.get)
        closest_distance_value = distances[closest_distance_vector]
        return closest_distance_value
    else:
        return MAXIMUM_DISTANCE_PENALTY


@Timer(text="Integer Reading: {:0.8f} seconds")
def experimental():
    g = get_world_state_experimental(area=AREA)
    for tile in search_tiles:
        flood_fill_search(tile, g)


@Timer(text="String Reading: {:0.8f} seconds")
def string_read():
    g = get_world_state(area=AREA)
    for tile in search_tiles:
        flood_fill_search(tile, g)


experimental()
string_read()

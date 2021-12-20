"""Attempting to create a flood fill search for water tiles
    """
from typing import Dict
from classes.ENUMS.block_codes import block_codes
from classes.Graph import graph, manhattan
from classes.Tile import Tile
from classes.Timer import Timer
from classes.Types import GridLocation
from classes.http_interface import get_world_state
from classes.misc_functions import get_build_coord
from constants import (
    MAXIMUM_DISTANCE_PENALTY,
    WATER_SEARCH_RADIUS,
)
import random

# g_start = get_world_state(paint_fence=True, area=AREA)


check_vertexes = []
X = 256
Z = 256

# generate building indexes around it
water_tile_list = []
for i in range(1000):
    water_tile_list.append((random.randint(1, 255), random.randint(1, 255)))

tile_map = []
for x_value in range(X):
    row = []
    for z_value in range(Z):

        block = Tile(x_value, z_value, 100, block_codes.PURPLE_WOOL.value)
        row.append(block)
    tile_map.append(row)

# Add the water values

for tile in water_tile_list:
    x_value = tile[0]
    z_value = tile[1]
    tile_map[x_value][z_value].material = block_codes.WATER.value
g = graph(tile_map)


def in_bounds(vector):
    (x_value, z_value) = vector
    if 0 <= x_value < X and 0 <= z_value < Z:
        return True
    else:
        return False


@Timer(text="Flood Fill Search: {:0.8f} seconds")
def flood_fill_search(location, g: graph):
    # If a location is IN water, return maximum distance
    build_locations = list(
        filter(
            in_bounds,
            get_build_coord(location=location, building_radius=3),
        )
    )
    if any(x in build_locations for x in water_tile_list):
        print("Building in water")
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
        print("Water in search area")
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
        print("Water not in search area")
        return MAXIMUM_DISTANCE_PENALTY


import collections


class Queue:
    def __init__(self):
        self.elements = collections.deque()

    def empty(self) -> bool:
        return not self.elements

    def put(self, x):
        self.elements.append(x)

    def get(self):
        return self.elements.popleft()


@Timer(text="BFS: {:0.8f} seconds")
def breadth_first_search(g, start):

    # narrow the graph
    search_x_start = start[0] - int(WATER_SEARCH_RADIUS / 2)

    search_area = []
    for x_value in range(search_x_start, start[0] + int(WATER_SEARCH_RADIUS / 2)):
        row = []
        for z_value in range(search_x_start, start[0] + int(WATER_SEARCH_RADIUS / 2)):
            row.append(g.tile_map[x_value][z_value])
        search_area.append(row)
    tmp_graph = graph(search_area)
    frontier = Queue()
    frontier.put(start)
    reached = {}
    reached[start] = True

    while not frontier.empty():
        current = frontier.get()

        if (
            tmp_graph.tile_map[current[0]][current[1]].material
            == block_codes.WATER.value
        ):
            return
        for next in tmp_graph.neighbors(current):
            if next not in reached:
                frontier.put(next)
                reached[next] = True


flood_fill_search((10, 10), g=g)
breadth_first_search(g, (10, 10))

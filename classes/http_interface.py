"""Functions to interact with the the HTTP interface"""

import numpy as np

from classes.Tile import Tile
from classes.Types import GridLocation
from classes.Graph import graph
from vendor.gdmc_http_client.interfaceUtils import setBlock
from vendor.gdmc_http_client.worldLoader import WorldSlice
import vendor.gdmc_http_client 


def get_world_state(paint_fence=False, area=(0, 0, 100, 60)) -> graph:
    """Get the world state in a graph representation

    Args:
        paint_fence (boolean): Paint a fence around the search area
        area (Tuple[int, int, int, int]): start x, start z, end x, end z
        of the search area

    Returns:
        graph: graph object representation of the search space

    """
    world_slice = WorldSlice(area)
    block_map, height_map = get_material_and_height_map(world_slice=world_slice)
    if paint_fence:
        mapUtils.paint_fence(worldSlice=world_slice, heightmap=height_map)
        world_slice = WorldSlice(area)
        block_map, height_map = get_material_and_height_map(world_slice=world_slice)
    input_space = calc_input_space(block_map=block_map, height_map=height_map)
    g_representation = graph(input_space)
    return g_representation


def calc_input_space(block_map: np.ndarray, height_map: np.ndarray) -> np.ndarray:
    """Convert data into format the graph object accepts

    Args:
        block_map (np.ndarray): Array containing material data
        height_map (np.ndarray): Array containing y index data

    Returns:
        [np.ndarray]: Array with above
    """
    input_space = []
    for x_value in range(len(block_map)):
        input_space_row = []
        for z_value in range(len(block_map[x_value])):
            block = Tile(
                x_value,
                z_value,
                height_map[x_value][z_value],
                block_map[x_value][z_value],
            )
            input_space_row.append(block)
        input_space.append(input_space_row)
    return np.array(input_space)


def calc_good_heightmap(world_slice) -> np.ndarray:
    """Calculates a heightmap ideal for building.
    Trees are ignored and water is considered ground.

    Args:
        worldSlice (WorldSlice): an instance of the WorldSlice class
        containing the raw heightmaps and block data

    Returns:
        any: numpy array containing the calculated heightmap
    """
    hm_mbnl = world_slice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    height_map_no_trees = hm_mbnl[:]
    area = world_slice.rect

    for x_value in range(area[2]):
        for z_value in range(area[3]):
            while True:
                y_value = height_map_no_trees[x_value, z_value]
                block = world_slice.getBlockAt(
                    (area[0] + x_value, y_value - 1, area[1] + z_value)
                )
                if block[-4:] == "_log":
                    height_map_no_trees[x_value, z_value] -= 1
                else:
                    break

    return np.array(np.minimum(hm_mbnl, height_map_no_trees))


def calculate_block_map(world_slice) -> np.ndarray:
    """Calculates a material block map based on a height map

    Args:
        world_slice ([type]): WorldSlice Object
        height_map (np.ndarray): Array containing Y index of the highest block.
    Returns:
        np.ndarray: 2 dimensional array containing the material at y index.
        Note Z is across, Z is down
    """
    height_map = calc_good_heightmap(world_slice)
    block_map = []
    area = world_slice.rect
    for x_value in range(area[2]):
        block_row = []
        for z_value in range(area[3]):
            y_value = height_map[x_value][z_value]
            material = world_slice.getBlockAt((x_value, y_value - 1, z_value))
            block_row.append(material)
        block_map.append(block_row)
    return np.array(block_map)


def get_material_and_height_map(world_slice):
    """Get array of materials at y index  and y index

    Args:
        world_slice ([type]): Worldslice object

    Returns:
        tuple[np.ndarray, np.ndarray]: Array of materials at y index and array of y index
    """
    height_map = calc_good_heightmap(world_slice=world_slice)
    block_map = calculate_block_map(world_slice=world_slice)
    return block_map, height_map


def paint_block(location, material: str) -> None:
    """Paints a block onto map at an X, Z, Y location)

    Args:
        location ([typle[int, int, int]]): X, Z and Y location of the marker
        material (str): String containing the material to be painted
    """
    setBlock(location[0], location[2], location[1], material)

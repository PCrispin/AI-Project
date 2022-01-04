""" Generates a list of building locations through genetic algorithms"""

import sys
import os
import random
from typing import Tuple
import itertools
from classes.ENUMS.biome_ids import biome_regions
from classes.ENUMS.block_codes import block_codes
from classes.Timer import Timer
from classes.building_locations import BuildingLocations
from classes.Graph import graph, print_all_fitness_graphs
from classes.http_interface import get_world_state
from classes.Location_Genome import LocationGenome
from classes.Population import Population
from classes.misc_functions import rectangles_overlap, teleport_player
from constants import (
    AREA,
    BIOME_BLOCK_MAP_DICTIONARY,
    BIOME_MAP_DICTIONARY,
    BLOCK_BATCH_SIZE,
    BUILDING_NUMBER,
    FOLIAGE_CLEARING_HEIGHT,
    GENERATIONS,
    MINECRAFT_USERNAME,
    POPULATION_SIZE,
    RANDOM_SEED,
)
from vendor.gdmc_http_client.interfaceUtils import placeBlockBatched, runCommand
from vendor.gdmc_http_client.worldLoader import WorldSlice


random.seed(RANDOM_SEED)


def run_epochs(g_representation: graph) -> BuildingLocations:
    """Runs epochs of genetic algorithm to return class containing ideal locations

    Args:
         g_representation(graph): A graphical representation of the search space

    Returns:
        Building_Locations: A class containing fitness building locations

    """
    # get the world slice to add to the building_locations

    locations = BuildingLocations(world_slice=WorldSlice(AREA))
    for _ in range(BUILDING_NUMBER):
        fitess = generate_building_location_through_genetic_algorithm(
            g_representation=g_representation
        )
        locations.add_building(fitess)
        g_representation.building_tiles.extend(locations.locations[-1].build_locations)
        g_representation.buildings_centres.append((fitess.x, fitess.z))
        g_representation.buildings_coords.append(
            locations.locations[-1].build_coordinates
        )

    determine_village_biome(locations=locations)
    return locations


def determine_village_biome(
    locations: BuildingLocations,
) -> Tuple[biome_regions, block_codes]:

    try:
        biome_lst = []
        for location in locations.locations:
            biome_id = locations.get_biome(location=location, y_index=100)
            biome_region = biome_regions(BIOME_MAP_DICTIONARY.get(biome_id))
            biome_lst.append(biome_region.value)
        best_biome = biome_regions(max(set(biome_lst), key=biome_lst.count))
        block_type = BIOME_BLOCK_MAP_DICTIONARY.get(best_biome)
        locations.biome_region = best_biome
        locations.variable_blocktype = block_type
    except ValueError:
        print("Biome Id not in BIOME_MAP_DICTIONARY - Maybe consider adding it? :D")
        locations.biome_region = biome_regions.DESERT
        locations.variable_blocktype = block_codes.SANDSTONE


def remove_foliage(g: graph, buildings: BuildingLocations):
    """Removes foliage from above the heightmap around the town location

    Args:
        g (graph): [description]
        buildings (BuildingLocations): [description]
    """

    all_building_coord = []
    for location in buildings.locations:
        all_building_coord.append(location.build_coordinates)
    x_min: int = min(all_building_coord, key=lambda t: t[0])[0]
    x_max: int = max(all_building_coord, key=lambda t: t[2])[2]
    z_min: int = min(all_building_coord, key=lambda t: t[1])[1]
    z_max: int = max(all_building_coord, key=lambda t: t[3])[3]

    for x_value in range(max(x_min, AREA[0]), min(x_max, AREA[2])):
        for z_value in range(max(x_min, AREA[1]), min(z_max, AREA[3])):
            for i in range(FOLIAGE_CLEARING_HEIGHT):
                placeBlockBatched(
                    x_value,
                    g.tile_map[x_value][z_value].z + i,
                    z_value,
                    block_codes.AIR.value,
                    BLOCK_BATCH_SIZE,
                )

    teleport_player(x_value=x_min, y_value=100, z_value=z_min)


def generate_building_location_through_genetic_algorithm(
    g_representation: graph,
) -> LocationGenome:
    """Generates a single building location through genetatic algorithms

    Args:
        g_representation (graph): A graphical representation of the search space

    Returns:
        location_genome: Fitess Geneome of the population
    """

    population = Population(
        init_random=True, p_size=POPULATION_SIZE, g_repesentation=g_representation
    )
    for _ in range(GENERATIONS):
        print(f"Generation {_}")
        population.run_tournament()
        population = population.next_generation()
    fitess_member = population.get_fitess_member()
    print(
        f"Found site (x, z) ({fitess_member.x},{fitess_member.z}) with build radius {fitess_member.building_radius}"
    )
    return fitess_member


def block_print():
    """Disable print outputs - debugging"""
    sys.stdout = open(os.devnull, "w")


def enable_print():
    """Disable print outputs - debugging"""
    sys.stdout = sys.__stdout__


@Timer(text="Program executed ran in {:.2f} seconds")
def main(debug=False, removefoliage=True):
    print("Starting Program")

    if not debug:
        block_print()
    g_start = get_world_state(area=AREA)

    # print_all_fitness_graphs(g=g_start)
    buildings = run_epochs(g_start)
    remove_overlapping_buildings(buildings)
    if removefoliage:
        remove_foliage(g=g_start, buildings=buildings)

    buildings.paint_buildings()

    if not debug:
        enable_print()


def remove_overlapping_buildings(buildings):
    check_order = list(itertools.product(buildings.locations, repeat=2))
    overlap = []
    for location in check_order:
        if location[0] == location[1]:
            overlap.append(False)
        else:
            overlap.append(
                rectangles_overlap(
                    location[0].build_coordinates, location[1].build_coordinates
                )
            )
    true_indexes = [i for i, x in enumerate(overlap) if x]
    if len(true_indexes) > 0:
        for i in true_indexes:
            site_1 = check_order[i][0]
            if site_1 in buildings.locations:
                buildings.locations.remove(site_1)
                remove_overlapping_buildings(buildings)
    else:
        return


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create a minecraft village through GA"
    )
    parser.add_argument(
        "--debug",
        metavar="path",
        required=False,
        help="Show debug output",
        default=True,
    )

    parser.add_argument(
        "--removefoliage",
        metavar="path",
        required=False,
        help="Remove Folliage",
        default=True,
    )
    args = parser.parse_args()
    main(debug=args.debug, removefoliage=args.removefoliage)

""" Generates a list of building locations through genetic algorithms"""

import sys
import os
import random
from classes.Timer import Timer
from classes.building_locations import BuildingLocations
from classes.Graph import graph
from classes.http_interface import get_world_state
from classes.Location_Genome import LocationGenome
from classes.Population import Population
from classes.misc_functions import rectangles_overlap
from constants import AREA, BUILDING_NUMBER, GENERATIONS, POPULATION_SIZE, RANDOM_SEED


random.seed(RANDOM_SEED)


def run_epochs(g_representation: graph) -> BuildingLocations:
    """Runs epochs of genetic algorithm to return class containing ideal locations

    Args:
         g_representation(graph): A graphical representation of the search space

    Returns:
        Building_Locations: A class containing fitness building locations

    """
    locations = BuildingLocations()
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
    return locations


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
        f"Found site (x, y, z) ({fitess_member.x},{fitess_member.z}) with build radius {fitess_member.building_radius}"
    )
    return fitess_member


def block_print():
    """Disable print outputs - debugging"""
    sys.stdout = open(os.devnull, "w")


def enable_print():
    """Disable print outputs - debugging"""
    sys.stdout = sys.__stdout__


import itertools


@Timer(text="Program executed ran in {:.2f} seconds")
def main(debug=False):
    print("Starting Program")

    if not debug:
        block_print()
    g_start = get_world_state(area=AREA)
    # print_all_fitness_graphs(g=g_start)
    buildings = run_epochs(g_start)
    remove_overlapping_buildings(buildings)
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
    args = parser.parse_args()
    main(debug=args.debug)

""" Generates a list of building locations through genetic algorithms

    Returns:
        [list] - List containing A location genomes containing best building locations,
        building location blocks, and fitness value.
    """


import numpy as np
from classes.building_locations import BuildingLocations
from classes.Graph import graph
from classes.http_interface import get_world_state
from classes.Location_Genome import LocationGenome
from classes.Population import Population


GENERATIONS = 10
BUILDING_NUMBER = 10
POPULATION_SIZE = 20
AREA = (0, 0, 128, 128)  # x position, z position, x size, z sizew


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
    return locations


def termination_criteria(std_fitness: list) -> bool:
    if len(std_fitness) > 5:

        if np.std(std_fitness[-5:]) < 100:
            return False
        else:
            print("Found Locaiton...")
            return True

    else:
        return True


def generate_building_location_through_genetic_algorithm(
    g_representation: graph,
) -> LocationGenome:
    """Generates a single building location through genetatic algorithms

    Args:
        g_representation (graph): A graphical representation of the search space

    Returns:
        location_genome: Fitess Geneome of the population
    """
    population_std_fitness = []
    population = Population(
        init_random=True, p_size=POPULATION_SIZE, g_repesentation=g_representation
    )
    should_terminate = True
    while should_terminate:

        population.run_tournament()
        population_std_fitness.append(
            population.get_population_fitness_standard_deviation()
        )
        should_terminate = termination_criteria(population_std_fitness)
        population = population.next_generation()
    fitess_member = population.get_fitess_member()
    return fitess_member


if __name__ == "__main__":
    g_start = get_world_state(paint_fence=True, area=AREA)
    # g_start.visualise()
    buildings = run_epochs(g_start)
    buildings.paint_buildings()

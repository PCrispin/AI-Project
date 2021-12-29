""" Generates a list of building locations through genetic algorithms

    Returns:
        [list] - List containing A location genomes containing best building locations,
        building location blocks, and fitness value.
    """


from classes.ENUMS.fitness import fitness_functions
from classes.building_locations import BuildingLocations
from classes.Graph import graph, print_all_fitness_graphs
from classes.http_interface import get_world_state
from classes.Location_Genome import LocationGenome
from classes.Population import Population
from constants import AREA, BUILDING_NUMBER, GENERATIONS, POPULATION_SIZE
import time


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
        f"Found site (x, y, z) ({fitess_member.x}, {fitess_member.ideal_y}, {fitess_member.z}) with build radius {fitess_member.building_radius}"
    )
    return fitess_member


if __name__ == "__main__":

    start = time.time()
    g_start = get_world_state(area=AREA)
    g_start.visualise(fitness=fitness_functions.HOUSE_DISTANCE)
    # print_all_fitness_graphs(g=g_start)
    buildings = run_epochs(g_start)
    buildings.paint_buildings()

    mins, sec = divmod(time.time() - start, 60)
    print(f"\n\nTOTAL RUN TIME: {mins:.0f}m {sec:.0f}s")

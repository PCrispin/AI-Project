"""Class containing location genome

    Returns:
        LocationGenome: Genome with building location
        information
"""

import random
from classes.Types import GridLocation
from constants import MAX_BUILDING_RADIUS


class LocationGenome:
    """Class for location genome"""

    def __init__(
        self,
        walled_vectors: list,  # prohibited squares
        graph_space: tuple,  # graph space where genes can occur
        grid_location: GridLocation = None,  # Previous x,z coord
        init_random=False,  # random genome
        building_radius: int = 1,
    ):
        self.walled_vectors: list = walled_vectors
        self.graph_space: GridLocation = graph_space
        self.fitness: int = 0
        self.water_distance_fitness: int = 0
        self.build_distance_fitness: int = 0
        self.flatness_fitness: int = 0
        self.building_radius: int = building_radius
        self.adjusted_fitness: int = 0  # adjusted fitness
        self.fitness_probability: int = 0  # Chance of selection
        self.build_locations: list = []
        self.ideal_y: int = 0
        if init_random:
            self.x, self.z = self._get_random_possible_coordinate()

        elif not init_random:
            self.x = grid_location[0]
            self.z = grid_location[1]

    def get_vector_coord(self) -> GridLocation:
        """Return vector cordinates of the genome

        Returns:
            GridLocation: the x, z location of the genome
        """
        return (self.x, self.z)

    def _get_possible_coordinate(self) -> list:
        possible_list = []
        for z_value in range(self.graph_space[1]):
            for x_value in range(self.graph_space[0]):
                possible_list.append((x_value, z_value))

        prohibited_coords = self.walled_vectors
        possible_coords = [
            item for item in possible_list if item not in prohibited_coords
        ]
        return possible_coords

    def _get_random_possible_coordinate(self) -> tuple:
        random_x_value = random.choice(
            range(
                (0 + MAX_BUILDING_RADIUS), (self.graph_space[0] - MAX_BUILDING_RADIUS)
            )
        )
        random_z_value = random.choice(
            range(
                (0 + MAX_BUILDING_RADIUS), (self.graph_space[1] - MAX_BUILDING_RADIUS)
            )
        )
        return (random_x_value, random_z_value)

    def _check_vector_possible(self) -> bool:
        location = (self.x, self.z)
        if location not in self.walled_vectors:
            return True
        else:
            return False

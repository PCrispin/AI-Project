"""Graph representation of the search space

    Returns:
        graph: graph object containg information about
        the search space
    """
import statistics
import numpy as np
from classes.ENUMS.block_codes import block_codes
from classes.Types import GridLocation, TileMap
from classes.location_genome import LocationGenome
from classes.misc_functions import get_build_coord
import numpy as np
import matplotlib.pyplot as plt


class graph:
    """Object representation of the TileMap"""

    def __init__(
        self,
        tile_map: TileMap,
    ):
        self.x: int = len(tile_map)
        self.z: int = len(tile_map[0])
        self.tile_map = tile_map
        self.water_tiles: list = []
        self.building_tiles: list = []
        self.create_tile_lists()

    def create_tile_lists(self):
        """Loops through tile map and adds water tiles to list"""

        for x_value in range(self.x):
            for z_value in range(self.z):
                if self.tile_map[x_value][z_value].material == block_codes.WATER.value:
                    self.water_tiles.append((x_value, z_value))

    def print_graph(self, show_z_index=False):
        """Prints a terminal representation of the grid graph
        Args:
            show_z_index (bool, optional): Shows Z index values on traversable vertexs.
            Defaults to False.
        """
        for _ in range(self.x):
            print("---", end="")
        print("\n")

        for z_value in range(self.z):
            for x_value in range(self.x):
                print(
                    self.tile_map[x_value][z_value].draw_tile(
                        show_z_index=show_z_index
                    ),
                    end="",
                )
            print("\n")
        for _ in range(self.x):
            print("---", end="")
        print("\n")

    def get_graph_space(self) -> GridLocation:
        """Return GridLocation of the search space"""
        return (self.x, self.z)

    def x_z_to_index(self, coord: GridLocation) -> int:
        """Converts GridLocation to an index value

        Args:
            coord (GridLocation): Gridlocation for conversion

        Returns:
            int: Index value of the vertex
        """
        return coord[0] + (coord[1] * self.x)

    def in_bounds_boolean(self, vector: GridLocation) -> bool:
        """Checks if a GridLocation is within boundaries of the grid space

        Args:
            vector (GridLocation): Gridlocation to check

        Returns:
            bool: True: within grid space, False if not
        """
        (x_value, z_value) = vector
        if 0 <= x_value < self.x and 0 <= z_value < self.z:
            return True
        else:
            return False

    def calculate_distance_from_water_vectors(self, location: GridLocation) -> float:
        """Calculates the average manhattan distance for a location from all water vectors

        Args:
            location (GridLocation): [description]

        Returns:
            Float: [description]
        """
        cum_distance = 0
        for water_location in self.water_tiles:
            cum_distance += manhattan(water_location, location)
        total_water_vectors = len(self.water_tiles)
        return cum_distance / total_water_vectors

    def calculate_distance_from_houses(self, location: GridLocation) -> float:
        """Calculates the average manhattan distance for a location from all house vectors

        Args:
            location (GridLocation): [description]

        Returns:
            Float: [description]
        """
        cum_distance = 0
        for building_location in self.building_tiles:
            cum_distance += manhattan(building_location, location)
        total_build_vectors = len(self.building_tiles)
        return cum_distance / total_build_vectors

    def calculate_flatness_from_location(self, build_list: list) -> float:
        """Return fitness value from a location based on fitness of
           the proposed location using standard deviation

        Args:
            build_list (list): blocks used to build location

        Returns:
            float: build fitness
        """
        z_indexes = []
        for tile in build_list:
            z_indexes.append(self.tile_map[tile[0], tile[1]].z)
        return np.std(z_indexes)

    def calculate_ideal_y_plane(self, build_list: list) -> int:
        """Return ideal y plane for building location

        Args:
            build_list (list): blocks used to build location

        Returns:
            int: [description]
        """
        y_indexes = []
        for tile in build_list:
            y_indexes.append(self.tile_map[tile[0], tile[1]].z)

        return int(statistics.mean(y_indexes))

    def visualise(self, autonormalize=True):
        """Creates plots to visualise the fitness map."""
        building_radius = 1

        water_fitness_map = []
        flatness_fitness_map = []

        # calculate the maximum water distance for all tiles

        for x_value in range(building_radius, self.x - building_radius):
            z_waters = []
            z_flatness = []
            for z_value in range(building_radius, self.z - building_radius):
                z_waters.append(
                    calculate_distance_fitness_from_water(
                        location=(x_value, z_value),
                        graph_representation=self,
                        building_radius=building_radius,
                    )
                )
                z_flatness.append(
                    calculate_flatness_fitness(
                        location=(x_value, z_value),
                        graph_representation=self,
                        building_radius=building_radius,
                    )
                )
            water_fitness_map.append(z_waters)
            flatness_fitness_map.append(z_flatness)
        w_f_m = np.array(water_fitness_map)
        f_f_m = np.array(flatness_fitness_map)

        if autonormalize:
            f_f_m = scale(f_f_m, 0, 1)
            w_f_m = scale(w_f_m, 0, 1)

        a_f_m = np.add(f_f_m, w_f_m)

        show_plot(f_f_m)
        show_plot(w_f_m)
        show_plot(a_f_m)


def calculate_distance_fitness_from_water(
    location: GridLocation,
    graph_representation: graph,
    building_radius: int = 3,
) -> float:
    max_distance: int = (
        max((graph_representation.x / 2), (graph_representation.z / 2)) * 1.5
    )
    build_coords = get_build_coord(
        (location[0], location[1]), building_radius=building_radius
    )

    in_water = any(x in build_coords for x in graph_representation.water_tiles)
    if in_water:
        return max_distance * 1.5
    else:
        return graph_representation.calculate_distance_from_water_vectors(
            (location[0], location[1])
        )


def calculate_flatness_fitness(
    location: GridLocation,
    graph_representation: graph,
    building_radius: int = 3,
):
    build_coords = get_build_coord(
        (location[0], location[1]), building_radius=building_radius
    )
    return graph_representation.calculate_flatness_from_location(build_coords)


def calculate_house_distance_fitness(
    location: GridLocation,
    graph_representation: graph,
    building_radius: int = 3,
) -> float:
    max_distance: int = (
        max((graph_representation.x / 2), (graph_representation.z / 2)) * 1.5
    )
    build_coords = get_build_coord(
        (location[0], location[1]), building_radius=building_radius
    )
    if any(x in build_coords for x in graph_representation.building_tiles):
        distance = max_distance
    else:
        distance = graph_representation.calculate_distance_from_houses(
            location=location
        )
    return distance


def manhattan(a_value, b_value):
    """Calculate manhattan distance value between two vectors

    Args:
        a_value ([type]): A vector
        b_value ([type]): Another vector

    Returns:
        [type]: Manhattan distance between two vectors
    """
    return sum(abs(val1 - val2) for val1, val2 in zip(a_value, b_value))


def scale(X, x_min, x_max):
    """Scales an array to a minimum value and maximum value

    Args:
        X ([type]): [description]
        x_min ([type]): [description]
        x_max ([type]): [description]

    Returns:
        [type]: [description]
    """
    nom = (X - X.min(axis=0)) * (x_max - x_min)
    denom = X.max(axis=0) - X.min(axis=0)
    denom[denom == 0] = 1
    return x_min + nom / denom


def surface_plot(matrix, **kwargs):
    # acquire the cartesian coordinate matrices from the matrix
    # x is cols, y is rows
    (x, y) = np.meshgrid(np.arange(matrix.shape[0]), np.arange(matrix.shape[1]))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(x, y, matrix, **kwargs)
    return (fig, ax, surf)


def show_plot(m):
    (fig, ax, surf) = surface_plot(m, cmap=plt.cm.coolwarm)

    fig.colorbar(surf)

    ax.set_xlabel("X (cols)")
    ax.set_ylabel("Y (rows)")
    ax.set_zlabel("Z (values)")

    plt.show()

"""Graph representation of the search space

    Returns:
        graph: graph object containg information about
        the search space
    """
import numpy as np
from classes.ENUMS.fitness import fitness_functions
from classes.Types import GridLocation, TileMap
from classes.misc_functions import (
    get_build_coord,
    rectangles_overlap,
    cut_out_bounds,
)
import matplotlib.pyplot as plt
from typing import List, Tuple

from constants import (
    IMAGE_DIR_FOLD,
    MAX_BUILDING_RADIUS,
    MAXIMUM_DISTANCE_PENALTY,
    MAXIMUM_HOUSE_DISTANCE_PENALTY,
    WATER_SEARCH_RADIUS,
)


class graph:
    """Object representation of the TileMap"""

    def __init__(
        self,
        tile_map: TileMap,
    ):
        self.x: int = len(tile_map)
        self.z: int = len(tile_map[0])
        self.tile_map: TileMap = tile_map
        self.water_tiles: list = []
        self.building_tiles: list = []
        self.buildings_coords = []
        self.buildings_centres = []
        self.create_tile_lists()

    def create_tile_lists(self):
        """Loops through tile map and adds water tiles to list"""
        for x_value in range(self.x):
            for z_value in range(self.z):
                if self.tile_map[x_value][z_value].material == 1:
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

    def calcuate_water_distance(self, location, building_radius):

        PENALTY = self._calculate_penalty(
            location=location,
            building_radius=building_radius,
            type=fitness_functions.WATER_DISTANCE,
        )

        if PENALTY:
            return MAXIMUM_DISTANCE_PENALTY

        radius = WATER_SEARCH_RADIUS // 2

        grid = (
            cut_out_bounds(location[0] - radius, self.x),
            cut_out_bounds(location[1] - radius, self.z),
            cut_out_bounds(location[0] + radius, self.x),
            cut_out_bounds(location[1] + radius, self.z),
        )

        min_distance = self.tile_map[grid[0]][grid[1]].manhattan_distance_to_water
        cum_distance = 0
        for x_value in range(grid[0], grid[2]):
            for z_value in range(grid[1], grid[3]):
                cum_distance += self.tile_map[x_value][
                    z_value
                ].manhattan_distance_to_water
                min_distance = min(
                    min_distance,
                    self.tile_map[x_value][z_value].manhattan_distance_to_water,
                )
        value = cum_distance / (x_value * z_value)
        return value

    def calculate_distance_from_houses(
        self, location: GridLocation, building_radius=MAX_BUILDING_RADIUS
    ) -> float:
        """Calculates the average manhattan distance for a location from all house vectors

        Args:
            location (GridLocation): [description]

        Returns:
            Float: [description]
        """

        PENALTY = self._calculate_penalty(
            location=location,
            building_radius=building_radius,
            type=fitness_functions.HOUSE_DISTANCE,
        )

        if PENALTY:
            return MAXIMUM_HOUSE_DISTANCE_PENALTY

        cum_distance = 0
        for building_location in self.buildings_centres:
            cum_distance += manhattan(location, building_location)

        return np.linalg.norm(np.array(location) - np.array(building_location))

    def _calculate_penalty(self, location, building_radius, type: fitness_functions):
        coords = (
            cut_out_bounds(location[0] - building_radius, self.x),
            cut_out_bounds(location[1] - building_radius, self.z),
            cut_out_bounds(location[0] + building_radius, self.x),
            cut_out_bounds(location[1] + building_radius, self.z),
        )

        if type == fitness_functions.HOUSE_DISTANCE:
            for building_coords in self.buildings_coords:
                if rectangles_overlap(coords, building_coords):
                    return True

        if type == fitness_functions.WATER_DISTANCE:
            for x_value in range(coords[0], coords[2]):
                for z_value in range(coords[1], coords[3]):
                    if self.tile_map[x_value][z_value].manhattan_distance_to_water == 0:
                        return True

        return False

    def calculate_flatness_from_location(
        self, location: GridLocation, building_radius: int
    ) -> float:
        """Return fitness value from a location based on fitness of
           the proposed location using standard deviation

        Args:
            build_list (list): blocks used to build location

        Returns:
            float: build fitness
        """

        build_locations = list(
            filter(
                self.in_bounds_boolean,
                get_build_coord(location=location, building_radius=building_radius),
            )
        )

        z_indexes = []
        for tile in build_locations:
            z_indexes.append(self.tile_map[tile[0], tile[1]].z)
        return np.std(z_indexes)

    def visualise(
        self,
        autonormalize=True,
        building_radius=MAX_BUILDING_RADIUS,
        fitness=fitness_functions,
    ):
        """Creates plots to visualise the fitness map."""

        if fitness == fitness_functions.WATER_BOOLEAN:
            return run_fitness_for_all_coords(
                autonormalize=autonormalize,
                fitness=fitness_functions.WATER_BOOLEAN,
                g=self,
            )

        if fitness == fitness_functions.WATER_DISTANCE:
            return run_bounded_fitness_for_all_coords(
                fitness=fitness_functions.WATER_DISTANCE,
                autonormalize=autonormalize,
                building_radius=building_radius,
                g=self,
            )

        if fitness == fitness_functions.HOUSE_DISTANCE:
            return run_bounded_fitness_for_all_coords(
                fitness=fitness_functions.HOUSE_DISTANCE,
                autonormalize=autonormalize,
                building_radius=building_radius,
                g=self,
                # show_plot=True,
            )
        if fitness == fitness_functions.FLATNESS:
            return run_bounded_fitness_for_all_coords(
                fitness=fitness_functions.FLATNESS,
                autonormalize=autonormalize,
                building_radius=building_radius,
                g=self,
            )


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


def show_plt(m):
    (fig, ax, surf) = surface_plot(m, cmap=plt.cm.coolwarm)

    fig.colorbar(surf)

    ax.set_xlabel("X (cols)")
    ax.set_ylabel("Y (rows)")
    ax.set_zlabel("Z (values)")

    plt.show()


def show_2d_heatmap(arr: np.array, filename: str):
    arr = arr.T  # transpose x and z axis
    heatmap, ax = plt.subplots()
    im = ax.imshow(
        arr,
        cmap=plt.cm.coolwarm,
        interpolation="nearest",
        origin="lower",
        aspect="auto",
    )
    ax.set(xlabel="Z coordinate", ylabel="X coordinate")
    heatmap.savefig(IMAGE_DIR_FOLD + "/" + filename + ".png")


def run_fitness_for_all_coords(
    fitness: fitness_functions, g: graph, autonormalize=True, show_plot=False
):
    fitness_function = []
    if fitness == fitness_functions.WATER_BOOLEAN:
        for x_value in range(0, g.x):
            tile = []
            for z_value in range(0, g.z):
                if g.tile_map[x_value][z_value].material == 1:
                    tile.append(1)
                else:
                    tile.append(0)
            fitness_function.append(tile)
        w_b_m = np.array(fitness_function)
        if autonormalize:
            w_b_m = scale(w_b_m, 0, 1)
        if show_plot:
            show_plot(w_b_m)
        show_2d_heatmap(w_b_m, fitness.value)
        return w_b_m


def run_bounded_fitness_for_all_coords(
    fitness: fitness_functions,
    g: graph,
    autonormalize=True,
    building_radius=MAX_BUILDING_RADIUS,
    show_plot=False,
):
    fitness_map = []
    # adjust the house fitness map with a mock house at 20, 20), with a build radius of 7
    location = (20, 20)
    coords: Tuple[int, int, int, int] = (
        cut_out_bounds(location[0] - building_radius, g.x),
        cut_out_bounds(location[1] - building_radius, g.z),
        cut_out_bounds(location[0] + building_radius, g.x),
        cut_out_bounds(location[1] + building_radius, g.z),
    )
    building_tiles = get_build_coord(location=location, building_radius=building_radius)
    g.building_tiles.extend(building_tiles)
    g.buildings_centres.append(location)
    g.buildings_coords = [tuple(coords)]
    for x_value in range(building_radius, g.x - building_radius):
        tile = []
        for z_value in range(building_radius, g.z - building_radius):
            if fitness == fitness_functions.WATER_DISTANCE:
                tile.append(
                    g.calcuate_water_distance(
                        (x_value, z_value), building_radius=building_radius
                    )
                )
            if fitness == fitness_functions.HOUSE_DISTANCE:
                tile.append(
                    g.calculate_distance_from_houses(
                        (x_value, z_value), building_radius=building_radius
                    )
                )
            if fitness == fitness_functions.FLATNESS:
                tile.append(
                    g.calculate_flatness_from_location(
                        (x_value, z_value), building_radius=building_radius
                    )
                )
        fitness_map.append(tile)
    f_m = np.array(fitness_map)
    if autonormalize:
        f_m = scale(f_m, 0, 1)
    if show_plot:
        show_plt(f_m)
    show_2d_heatmap(f_m, fitness.value)
    g.buildings_coords = []  # clean up the building tiles
    return f_m


def print_all_fitness_graphs(g: graph):
    fitness_maps = []

    for fitness in fitness_functions:
        fitness_maps.append(g.visualise(fitness=fitness))
    f_m = np.add(fitness_maps[0], fitness_maps[1])
    f_m = scale(f_m, 0, 1)
    show_plot(f_m)

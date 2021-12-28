"""Graph representation of the search space

    Returns:
        graph: graph object containg information about
        the search space
    """
import numpy as np
from classes.Types import GridLocation, TileMap
from classes.misc_functions import get_build_coord, rectangles_overlap, cut_out_bounds
import matplotlib.pyplot as plt
from typing import List, Tuple

from constants import (
    IMAGE_DIR_FOLD,
    MAX_BUILDING_RADIUS,
    MAXIMUM_DISTANCE_PENALTY,
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
        self.tile_map : TileMap = tile_map
        self.water_tiles: list = []
        self.building_tiles: list = []
        self.buildings_coords : List[Tuple[int,int,int,int]] = []
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
            location=location, building_radius=building_radius
        )

        if PENALTY:
            return MAXIMUM_DISTANCE_PENALTY

        radius = WATER_SEARCH_RADIUS // 2

        grid = (
            cut_out_bounds(location[0] - radius, self.x),
            cut_out_bounds(location[1] - radius, self.z),
            cut_out_bounds(location[0] + radius, self.x),
            cut_out_bounds(location[1] + radius, self.z)   
            )

        min_distance = self.tile_map[grid[0]][grid[1]].manhattan_distance_to_water

        for x_value in range(grid[0], grid[2]):
            for z_value in range(grid[1], grid[3]):
                min_distance = min(min_distance, self.tile_map[x_value][z_value].manhattan_distance_to_water)

        return min_distance

    def calcuate_water_distance_orig(self, location, building_radius):

        PENALTY = self._calculate_penalty(
            location=location, building_radius=building_radius
        )

        if PENALTY:
            return MAXIMUM_DISTANCE_PENALTY

        start_vertex = (
            location[0] - int(WATER_SEARCH_RADIUS / 2),
            location[1] - int(WATER_SEARCH_RADIUS / 2),
        )

        check_vertexes = []
        for width in range(0, WATER_SEARCH_RADIUS):
            for height in range(0, WATER_SEARCH_RADIUS):
                check_vertexes.append(
                    (start_vertex[0] + width, start_vertex[1] + height)
                )

        search_vertexs = list(filter(self.in_bounds_boolean, check_vertexes))

        if any(x in search_vertexs for x in self.water_tiles):
            # get commonalities in both lists
            water_tiles_in_search_radius = list(
                set(search_vertexs).intersection(self.water_tiles)
            )

            distances = {}
            for tile in water_tiles_in_search_radius:
                distances[tile] = manhattan(tile, location)
            closest_distance_vector = min(distances, key=distances.get)
            closest_distance_value = distances[closest_distance_vector]
            return closest_distance_value
        else:
            return MAXIMUM_DISTANCE_PENALTY

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
            location=location, building_radius=building_radius
        )

        if PENALTY:
            return MAXIMUM_DISTANCE_PENALTY

        cum_distance = 0
        for building_location in self.building_tiles:
            cum_distance += manhattan(building_location, location)
        total_build_vectors = len(self.building_tiles)
        return cum_distance / total_build_vectors

    def _calculate_penalty(self, location, building_radius):
        coords = (
              cut_out_bounds(location[0] - building_radius, self.x)
            , cut_out_bounds(location[1] - building_radius, self.z)
            , cut_out_bounds(location[0] + building_radius, self.x)
            , cut_out_bounds(location[1] + building_radius, self.z)
            )

        for building_coords in self.buildings_coords:
            if rectangles_overlap(coords, building_coords):
                return True

        for x_value in range(coords[0], coords[2]):
            for z_value in range(coords[1], coords[3]):
                if self.tile_map[x_value][z_value].manhattan_distance_to_water == 0:
                    return True

        return False

    def _calculate_penalty_orig(self, location, building_radius):
        build_locations = list(
            filter(
                self.in_bounds_boolean,
                get_build_coord(location=location, building_radius=building_radius),
            )
        )

        if any(x in build_locations for x in self.water_tiles or self.building_tiles):
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
        PENALTY = self._calculate_penalty(
            location=location, building_radius=building_radius
        )

        if PENALTY:
            return MAXIMUM_DISTANCE_PENALTY

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
        self, autonormalize=True, building_radius=MAX_BUILDING_RADIUS, fitness="water"
    ):
        """Creates plots to visualise the fitness map."""

        if fitness == "water":
            water_boolean = []
            for x_value in range(0, self.x):
                z_waters = []
                for z_value in range(0, self.z):
                    if self.tile_map[x_value][z_value].material == 1:
                        z_waters.append(1)
                    else:
                        z_waters.append(0)
                water_boolean.append(z_waters)
            w_b_m = np.array(water_boolean)
            if autonormalize:
                w_b_m = scale(w_b_m, 0, 1)
            show_plot(w_b_m)
            show_2d_heatmap(w_b_m, "water_boolean")

        if fitness == "water_distance":
            water_fitness_map = []
            for x_value in range(building_radius, self.x - building_radius):
                z_waters = []
                for z_value in range(building_radius, self.z - building_radius):
                    z_waters.append(
                        self.calcuate_water_distance(
                            (x_value, z_value), building_radius=building_radius
                        )
                    )
            water_fitness_map.append(z_waters)
            w_f_m = np.array(water_fitness_map)
            if autonormalize:
                w_f_m = scale(w_f_m, 0, 1)
            show_plot(w_f_m)
            show_2d_heatmap(w_f_m, "water_fitness")

        if fitness == "flatness":
            flatness_fitness_map = []
            for x_value in range(building_radius, self.x - building_radius):
                y_flatness = []
                for z_value in range(building_radius, self.z - building_radius):
                    y_flatness.append(
                        calculate_flatness_fitness(
                            location=(x_value, z_value),
                            graph_representation=self,
                            building_radius=building_radius,
                        )
                    )
            flatness_fitness_map.append(y_flatness)
            f_f_m = np.array(flatness_fitness_map)
            if autonormalize:
                f_f_m = scale(f_f_m, 0, 1)
            show_plot(f_f_m)
            show_2d_heatmap(f_f_m, "flatness_fitness")


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

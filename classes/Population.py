"""Population Class to return best build location

  Returns:
        Population: [A population with children from the preceeding population,
        evolved through genetic algorithm]
"""
from operator import attrgetter
from numpy import random
import numpy as np
from scipy.stats import multivariate_normal
from classes.Graph import (
    calculate_flatness_fitness,
    calculate_house_distance_fitness,
    graph,
)

from classes.Location_Genome import LocationGenome
from classes.Timer import Timer
from classes.misc_functions import get_build_coord
from sklearn.preprocessing import minmax_scale

from constants import (
    DEFAULT_MUTATION_RATE,
    DEFAULT_POPULATION_SIZE,
    MAX_BUILDING_RADIUS,
    MIN_BUILDING_RADIUS,
)


class Population:
    """Population class for location genome searching"""

    @Timer(text="Population Generated in {:.2f} seconds")
    def __init__(
        self,
        g_repesentation: graph,
        p_size=DEFAULT_POPULATION_SIZE,
        init_random=False,
        fitness_water_distance=True,
        fitness_building_location=False,
    ):
        self.p_size = p_size
        self.members = []
        self.graph = g_repesentation
        self.prob_mutation = DEFAULT_MUTATION_RATE
        self.total_fitness = 0
        self.fitness_probabilities: list = []

        if init_random:
            for _ in range(self.p_size):
                member = LocationGenome(
                    graph_space=(self.graph.x, self.graph.z),
                    init_random=True,
                    building_radius=random.randint(
                        MIN_BUILDING_RADIUS, MAX_BUILDING_RADIUS
                    ),
                )
                self.add_member(member)

    def add_member(self, location: LocationGenome):
        """Adds a member to the population

        Args:
            location (LocationGenome): [Member to be added]
        """
        self.members.append(location)

    @Timer(text="Next Generation Generated in {:.2f} seconds")
    def next_generation(self):
        """Creates the next generation"""

        child = Population(
            g_repesentation=self.graph,
            p_size=self.p_size,
            init_random=False,
        )

        fitess_member = self.get_fitess_member()
        child.add_member(fitess_member)  # add fitess members to the new population
        self.members.remove(
            fitess_member
        )  # remove fitess child from the selection pool

        for _ in range(self.p_size - 1):
            selection = self._selection()
            if random.uniform(0.0, 1.0) < self.prob_mutation:
                mutation = self._mutate(location=selection)
                child.add_member(mutation)
            else:
                child.add_member(selection)
        self._clear_population_fitness_values()
        return child

    @Timer(text="Tournament Ran in {:.2f} seconds")
    def run_tournament(self):
        """Calculates the fitness of the members

        Returns:
            [type]: [description]
        """
        self._run_fitness()
        self._create_adjusted_fitnesses()
        return self.total_fitness

    def _create_adjusted_fitnesses(self):
        self.total_fitness: int = sum(c.fitness for c in self.members)
        for member in self.members:
            member.adjusted_fitness = self.total_fitness / member.fitness

    def _selection(self):
        overallfitness = sum(c.adjusted_fitness for c in self.members)
        pick = random.uniform(0.0, overallfitness)
        for i in range(0, len(self.members)):
            pick -= self.members[i].adjusted_fitness
            if pick < 0:
                return self.members[i]

    def _run_fitness(self) -> None:
        """Calculates the population fitness"""

        water_distance_fitness = []
        if len(self.graph.water_tiles) != 0:
            for member in self.members:
                if len(self.graph.water_tiles) != 0:
                    water_fitness = self.graph.calcuate_water_distance_experimental(
                        location=(member.x, member.z)
                    )
                    member.water_distance_fitness = water_fitness
                    water_distance_fitness.append(water_fitness)
            water_distance_fitness = minmax_scale(
                water_distance_fitness, feature_range=(1, 2), axis=0
            )
            for i in range(len(self.members)):
                self.members[i].fitness += water_distance_fitness[i] * 2
                if self.members[i].fitness == 0:
                    print("yikes")

    def _clear_population_fitness_values(self):
        """Clears all population fitness values"""
        for member in self.members:
            member.fitness = 0
            member.water_fitness = 0
            member.adjusted_fitness = 0
            member.build_distance_fitness = 0
            member.fitness_probability = 0

    def _get_mutation_filter(self, building_radius: int) -> np.array:
        """Creates a 2D gaussian distribution and randomly generates a
        2D vector filter for mutaiton

        Args:
            building_radius (int): [description]
        """
        # Data
        x_values = np.linspace(-10, 10, building_radius)
        y_values = np.linspace(-10, 10, building_radius)
        X_values, Y_values = np.meshgrid(x_values, y_values)

        # Multivariate Normal
        mu_x = np.mean(x_values)
        sigma_x = np.std(x_values)
        mu_y = np.mean(y_values)
        sigma_y = np.std(y_values)
        r_v = multivariate_normal([mu_x, mu_y], [[sigma_x, 0], [0, sigma_y]])

        # Probability Density
        pos = np.empty(X_values.shape + (2,))
        pos[:, :, 0] = X_values
        pos[:, :, 1] = Y_values
        p_d = r_v.pdf(pos)
        total = np.sum(p_d)
        pd_prob_map = p_d / total
        tmp = 1 - pd_prob_map
        tmp = tmp / np.sum(tmp)
        linear_idx = np.random.choice(tmp.size, p=tmp.ravel() / float(tmp.sum()))
        x_values, y_values = np.unravel_index(linear_idx, tmp.shape)
        # convert to vector filter
        x_values = x_values - (building_radius // 2)
        z_values = y_values - (building_radius // 2)
        return np.array(x_values, z_values)

    def _mutate(self, location: LocationGenome):
        """Mutates a gene based on gaussian distribution"""
        mutation_filter = self._get_mutation_filter(location.building_radius)
        new_location = (location.x, location.z) + mutation_filter
        building_size = random.randint(MIN_BUILDING_RADIUS, MAX_BUILDING_RADIUS)
        mutation = LocationGenome(
            graph_space=(self.graph.x, self.graph.z),
            grid_location=new_location,
            building_radius=building_size,
        )
        if self.graph.in_bounds_boolean(new_location):
            return mutation
        else:
            return location

    def get_fitess_member(self) -> LocationGenome:
        """Return the fitess member of the population

        Returns:
            LocationGenome: [Member with the best scoring fitness]
        """
        fitess = min(self.members, key=attrgetter("fitness"))
        build_coords = get_build_coord(
            location=(fitess.x, fitess.z), building_radius=fitess.building_radius
        )
        ideal_y = 100
        fitess.ideal_y = ideal_y
        return fitess

    def get_population_fitness_standard_deviation(self) -> float:
        population_fitness = []
        for member in self.members:
            population_fitness.append(member.adjusted_fitness)
        return np.std(population_fitness, axis=0)

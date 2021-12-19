"""Class containing all building locations and operations
    on the building sites
 """
from classes.ENUMS.block_codes import block_codes
from classes.Location_Genome import LocationGenome
from classes.misc_functions import get_build_coord

import vendor.gdmc_http_client.interfaceUtils

USE_BATCH_PAINTING = True


class BuildingLocations:
    """Class containing all proposed building locations"""

    def __init__(self) -> None:
        self.total_fitness = 0
        self.water_fitness = 0
        self.building_fitness = 0
        self.flatness_fitness = 0
        self.locations = []

    def add_building(self, location: LocationGenome):
        """Adds a building location to the class

        Args:
            location (LocationGenome): Building Locations
        """
        build_locations = get_build_coord(
            location=location.get_vector_coord(),
            building_radius=location.building_radius,
        )
        location.build_locations = build_locations
        self.locations.append(location)

    def evaluate(self):
        """Evaluates all building locations"""
        for member in self.locations:
            self.total_fitness += member.fitness
            self.water_fitness += member.water_distance_fitness
            self.building_fitness += member.building_distance_fitness
            self.flatness_fitness += member.flatness_fitness

    def paint_buildings(self):
        """Paints building platforms onto the minecraft world"""
        if USE_BATCH_PAINTING:
            for location in self.locations:
                for tile in location.build_locations:
                    vendor.gdmc_http_client.interfaceUtils.placeBlockBatched(
                        tile[0],
                        location.ideal_y,
                        tile[1],
                        block_codes.RED_WOOL.value,
                        100,
                    )
                    for i in range(location.ideal_y + 1, 50):
                        vendor.gdmc_http_client.interfaceUtils.placeBlockBatched(
                            tile[0],
                            location.ideal_y + i,
                            tile[1],
                            block_codes.AIR.value,
                            100,
                        )
        vendor.gdmc_http_client.interfaceUtils.sendBlocks()

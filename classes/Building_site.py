from classes.ENUMS.orientations import orientations
from classes.Building import building
from classes.Bool_map import bool_map
from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_names import building_names
from constants import VISITS_PER_BUILDING_TYPE
from typing import Tuple, List
from sys import maxsize
import time


class building_site(object):
    AREA_EXPANDED_MARGIN = 5

    """Specifics of a building instance"""
    x_center = 0
    z_center = 0
    y_min = 0

    coords = (0, 0, 0, 0)
    area_expanded = (0, 0, 0, 0)

    x_zero = 0
    z_zero = 0
    x_factor = 1
    z_factor = 1

    building_name = building_names.APPLE_STORE
    building_type = building_types.UNKNOWN
    orientation = orientations.SOUTH

    width = 0
    depth = 0
    final_x_length = 0
    final_z_length = 0
    raw_x_length = 0
    raw_z_length = 0

    area = 0

    door_location = 0
    sign_location = 0

    repeaterXs = []
    repeaterZs = []

    building_map_x_index = 0
    building_map_z_index = 2

    def __init__(
        self,
        building: building,
        x_center: int,
        z_center: int,
        orientation: orientations,
        required_width: int = 0,
        required_depth: int = 0,
    ):
        self.x_center = x_center
        self.z_center = z_center
        self.building_type = building.type
        self.building_name = building_names(building.id)
        self.orientation = orientation

        self.width = building.width
        self.depth = building.depth
        self.area = self.width * self.depth

        if orientation in (orientations.NORTH, orientations.SOUTH):
            self.raw_x_length = building.width
            self.raw_z_length = building.depth
            self.repeaterXs, self.repeaterZs = building.getRepeaters(
                required_width, required_depth
            )
            building_map_x_index = 0
            building_map_z_index = 2
        else:
            self.raw_x_length = building.depth
            self.raw_z_length = building.width
            self.repeaterZs, self.repeaterXs = building.getRepeaters(
                required_width, required_depth
            )
            self.building_map_x_index = 2
            self.building_map_z_index = 0

        self.final_x_length = self.raw_x_length + len(self.repeaterXs) - 1
        self.final_z_length = self.raw_z_length + len(self.repeaterZs) - 1
        self.area = self.final_x_length * self.final_z_length

        self.x_factor, self.z_factor = ((-1, 1), (-1, -1), (1, -1), (1, 1))[
            orientation.value
        ]  # w,n,e,s

        self.x_zero = x_center + (-1 * self.x_factor * int(self.final_x_length / 2))
        self.z_zero = z_center + (-1 * self.z_factor * int(self.final_z_length / 2))

        x_end = self.x_zero + (self.x_factor * self.final_x_length)
        z_end = self.z_zero + (self.z_factor * self.final_z_length)

        self.coords = (
            min(self.x_zero, x_end),
            min(self.z_zero, z_end),
            max(self.x_zero, x_end),
            max(self.z_zero, z_end),
        )
        self.area_expanded = (
            self.coords[0] - self.AREA_EXPANDED_MARGIN,
            self.coords[1] - self.AREA_EXPANDED_MARGIN,
            self.final_x_length + 2 * self.AREA_EXPANDED_MARGIN,
            self.final_z_length + 2 * self.AREA_EXPANDED_MARGIN,
        )

        if orientation in (orientations.NORTH, orientations.SOUTH):
            self.door_location = (
                self.x_center,
                self.side_wall_coordinate(orientation) + self.z_factor,
            )
            self.sign_location = (
                self.door_location[0] + self.x_factor * 4,
                self.door_location[1],
            )
        else:
            self.door_location = (
                self.side_wall_coordinate(orientation) + self.x_factor,
                self.z_center,
            )
            self.sign_location = (
                self.door_location[0],
                self.door_location[1] + self.z_factor * 4,
            )

        return

    def set_altitude(self, floor: int):
        self.y_min = floor

    def side_wall_coordinate(self, side: orientations) -> int:
        return self.coords[side.value]  # w,n,e,s

    def map_coords_to_site_coords(self, x: int, y: int, z: int) -> Tuple[int, int, int]:
        # coords undergo translation and rotation
        return (
            self.x_zero + self.x_factor * x,
            self.y_min + y,
            self.z_zero + self.z_factor * z,
        )

    def get_description(self) -> str:
        return f"{self.building_name.name} built at [{self.coords[0]},{self.coords[1]}] size: [{self.final_x_length},{self.final_z_length}] at height {self.y_min}"

    def calc_adjacent_location(
        self,
        buildOnWhichSide: orientations,
        gapBetweenBuildings: int,
        orientation: orientations,
        building: building,
        requiredWidth: int = -1,
        requiredDepth: int = -1,
    ) -> Tuple[int, int]:

        factorFrom = (-1, -1, 1, 1)[buildOnWhichSide.value]  # w,n,e,s
        factorToReverse = (1, 1, -1, -1)[orientation.value]  # w,n,e,s

        if orientation in (orientations.NORTH, orientations.SOUTH):
            half_x = int(building.width / 2)  # TODO - Should be final width
            half_z = int(building.depth / 2)
        else:
            half_x = int(building.depth / 2)
            half_z = int(building.width / 2)

        if buildOnWhichSide in (orientations.NORTH, orientations.SOUTH):
            x_center = self.side_wall_coordinate(orientation) + half_x * factorToReverse
            z_center = (
                self.side_wall_coordinate(buildOnWhichSide)
                + (gapBetweenBuildings + 1 + half_z) * factorFrom
            )
        else:
            x_center = (
                self.side_wall_coordinate(buildOnWhichSide)
                + (gapBetweenBuildings + 1 + half_x) * factorFrom
            )
            z_center = self.side_wall_coordinate(orientation) + half_z * factorToReverse

        return x_center, z_center

    @classmethod
    def move_location(
        self, location: Tuple[int, int], direction: orientations, distance: int
    ) -> Tuple[int, int]:
        factor = (-1, -1, 1, 1)[direction.value]  # w,n,e,s

        if direction in (orientations.NORTH, orientations.SOUTH):
            return location[0], location[1] + factor * distance
        else:
            return location[0] + factor * distance, location[1]

    @classmethod
    def get_locations(
        self,
        centers: List[Tuple[int, int]],
        radii: List[int],
        world_map: bool_map,
        drive_length: int,
    ) -> Tuple[
        List[orientations],  # building_orientations
        List[Tuple[int, int]],  # door_locations
        List[Tuple[Tuple[int, int], Tuple[int, int]]],  # roads
    ]:

        n_sites = len(centers)

        average_location = (0, 0)
        for location in centers:
            average_location = (
                average_location[0] + location[0],
                average_location[1] + location[1],
            )
        average_location = int(average_location[0] / n_sites), int(
            average_location[1] / n_sites
        )

        # Make sure building is facing the center of the village, if possible.
        direction_preferences = []
        for location in centers:
            if average_location[0] - location[0] > 0:
                e_w_preference = (orientations.EAST, orientations.WEST)
            else:
                e_w_preference = (orientations.WEST, orientations.EAST)

            if average_location[1] - location[1] > 0:
                n_s_preference = (orientations.SOUTH, orientations.NORTH)
            else:
                n_s_preference = (orientations.NORTH, orientations.SOUTH)

            if abs(average_location[0] - location[0]) < abs(
                average_location[1] - location[1]
            ):
                direction_preferences.append(
                    (
                        e_w_preference[0],
                        n_s_preference[0],
                        e_w_preference[1],
                        n_s_preference[1],
                    )
                )
            else:
                direction_preferences.append(
                    (
                        n_s_preference[0],
                        e_w_preference[0],
                        n_s_preference[1],
                        e_w_preference[1],
                    )
                )

        building_orientations = []
        door_locations = []

        for location_index in range(n_sites):
            chosen = False
            for direction_preference in direction_preferences[location_index]:
                door_locations_candidate = building_site.move_location(
                    centers[location_index],
                    direction_preference,
                    radii[location_index] + drive_length,
                )

                if world_map.get_avoid_value(
                    door_locations_candidate[0], door_locations_candidate[1]
                ):
                    if world_map.get_avoid_water_value(
                        door_locations_candidate[0], door_locations_candidate[1]
                    ):
                        print(
                            f"Site {centers[location_index]}: potential door at {door_locations_candidate} blocked by water."
                        )
                    else:
                        print(
                            f"Site {centers[location_index]}: potential door at {door_locations_candidate} blocked by other building."
                        )
                else:
                    building_orientations.append(direction_preference)
                    door_locations.append(door_locations_candidate)
                    chosen = True
                    break
            if not chosen:
                raise Exception(
                    f"Building {centers[location_index]} has no possible door locations!"
                )

        roads = []

        for site1 in range(n_sites):  # functional_indices:
            for site2 in range(n_sites):  # functional_indices:
                if site1 != site2:
                    if (door_locations[site1], door_locations[site2]) not in roads and (
                        door_locations[site2],
                        door_locations[site1],
                    ) not in roads:
                        roads.append((door_locations[site1], door_locations[site2]))

        return building_orientations, door_locations, roads

    @classmethod
    def calc_building_types(
        self, distances: List[List[int]], number_of_families_in_a_flat: int
    ) -> List[Tuple[int, building_types]]:

        start_bfs = time.time()

        site_count = len(distances)
        locations_availble = list(range(site_count))

        # use only fully connected.  Any connected to network will be fully connected to all.
        site_roads_count = [[i] for i in range(site_count)]
        for site1 in locations_availble:
            for site2 in locations_availble:
                if site1 != site2 and distances[site1][site2]:
                    if site2 not in site_roads_count[site1]:
                        site_roads_count[site1].append(site2)
                    if site1 not in site_roads_count[site2]:
                        site_roads_count[site2].append(site1)

        locations_availble = []
        for site_road_count in site_roads_count:
            if len(site_road_count) > len(locations_availble):
                locations_availble = site_road_count

        site_count = len(locations_availble)

        if site_count < 3:
            raise TimerError(
                f"Not enough building sites! Some sites may have been removed due to no roads."
            )
        elif site_count < 10:
            building_types_in_village = []
            building_types_in_village.append(building_types.FACTORY)
            building_types_in_village.append(building_types.SHOP)
            building_types_in_village.append(building_types.FLATS)

            for h in range(site_count - 3):
                building_types_in_village.append(building_types.HOUSE)
        else:
            building_types_in_village = [building_types.TOWN_HALL]
            building_allocations = site_count - 1
            for index in range(building_allocations // 9):
                building_types_in_village.append(building_types.FACTORY)
                building_types_in_village.append(building_types.SHOP)
                building_types_in_village.append(building_types.RESTAURANT)
                building_types_in_village.append(building_types.FLATS)
                for h in range(5):
                    building_types_in_village.append(building_types.HOUSE)
            for h in range(building_allocations % 9):
                building_types_in_village.append(building_types.HOUSE)

        buildings_available_no_houses = list(
            filter(lambda x: x != building_types.HOUSE, building_types_in_village)
        )
        no_of_houses = site_count - len(buildings_available_no_houses)

        chosen_house_locations = []

        class attempt_details:
            def __init__(
                self,
                parent,
                location_index: int,
                building: building_types,
                is_top_node: bool = False,
            ):
                self.parent = parent
                self.location_index = location_index
                self.building = building
                self.is_top_node = is_top_node

            @classmethod
            def get_top_node(cls):
                return cls(None, -1, building_types.UNKNOWN, True)

        ################################################################################################################
        # find places for houses in step 1.  This is done first so that the following is not considered separately:
        # {HouseA in Location1, HouseB in Location2} and {HouseB in Location1, HouseA in Location2}
        # Step1 equates HouseA and HouseB as the same and so saves processing time
        # If only bfs_step2 was used, A and B would be considered as different entities
        def recursive_bfs_step1(
            attempt: attempt_details, house_count: int, locations_list: List[int]
        ) -> Tuple[int, List[Tuple[int, building_types]]]:
            if house_count == 0:
                return recursive_bfs_step2(
                    attempt, buildings_available_no_houses, locations_list
                )

            winning_score = maxsize
            available_locations = len(locations_list) - house_count + 1

            for i in range(available_locations):
                if house_count == no_of_houses and winning_score != maxsize:
                    mins, sec = divmod(time.time() - start_bfs, 60)
                    print(
                        f"Find optimum location {100*i/available_locations:.0f}% complete  {mins:.0f}m {sec:.0f}s Winning score: {winning_score}"
                    )

                location = locations_list.pop(i)

                candidate_score, candidate_building_locations = recursive_bfs_step1(
                    attempt_details(attempt, location, building_types.HOUSE),
                    house_count - 1,
                    locations_list,
                )

                locations_list.insert(i, location)

                if candidate_score < winning_score:
                    winning_score = candidate_score
                    winning_building_locations = candidate_building_locations

            return winning_score, winning_building_locations

        ################################################################################################################
        def recursive_bfs_step2(
            attempt: attempt_details,
            buildings_list: List[building_types],
            locations_list: List[int],
        ) -> Tuple[int, List[Tuple[int, building_types]]]:

            if not locations_list:

                function_building_locations = []
                house_location_adresses = []
                building_locations = []
                while not attempt.is_top_node:
                    building_locations.append(
                        (attempt.location_index, attempt.building)
                    )
                    if attempt.building == building_types.HOUSE:
                        house_location_adresses.append(attempt.location_index)
                    elif attempt.building == building_types.FLATS:
                        flat_address = attempt.location_index
                    else:
                        function_building_locations.append(
                            (attempt.location_index, attempt.building)
                        )
                    attempt = attempt.parent

                total_distance = 0
                for (
                    candidate_address,
                    candidate_building,
                ) in function_building_locations:
                    visit_count = VISITS_PER_BUILDING_TYPE[candidate_building.value]

                    for house_address in house_location_adresses:
                        total_distance += (
                            visit_count * distances[candidate_address][house_address]
                        )
                    total_distance += (
                        visit_count
                        * number_of_families_in_a_flat
                        * distances[candidate_address][flat_address]
                    )

                return total_distance, building_locations

            winning_score = maxsize
            winning_building_locations = []

            location = locations_list.pop(0)

            for i in range(len(buildings_list)):

                building = buildings_list.pop(i)

                candidate_score, candidate_building_locations = recursive_bfs_step2(
                    attempt_details(attempt, location, building),
                    buildings_list,
                    locations_list,
                )

                buildings_list.insert(1, building)

                if candidate_score < winning_score:
                    winning_score = candidate_score
                    winning_building_locations = candidate_building_locations

            locations_list.insert(0, location)

            return winning_score, winning_building_locations

        ################################################################################################################

        total_distance, building_location_types = recursive_bfs_step1(
            attempt_details.get_top_node(), no_of_houses, locations_availble
        )

        print(f"Total distance: {total_distance}")
        for building_location_type in building_location_types:
            print(
                f"Building location: {building_location_type[0]} -> {building_location_type[1].name}"
            )
        for index in range(len(site_roads_count)):
            if not site_roads_count:
                print(f"Building location: {index} -> NONE due to no roads.")

        mins, sec = divmod(time.time() - start_bfs, 60)
        print(f"\n\nTotal Time elapsed BFS: {mins:.0f}m {sec:.0f}s")

        return building_location_types

from classes.ENUMS.orientations import orientations
from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_names import building_names
from classes.ENUMS.block_codes import block_codes
from classes.Builder import Builder
from classes.Buildings import buildings
from classes.Building_site import building_site
from classes.AStar import find_routes, MAX_DETOUR, A_BIG_NUMBER
from vendor.gdmc_http_client.interfaceUtils import placeBlockBatched, sendBlocks, runCommand, getBlock
import numpy as np
from sys import maxsize 
import sys
from typing import List, Tuple
from data.roads_routes import existing_roads_routes
import time

PERCENTAGE_OF_RESIDENTIAL = 0.6
BLOCK_BATCH_SIZE = 1000
DRAW_HOUSES_ON = False #False if getBlock(60, 70, -491) == "minecraft:stone" else True
USE_SAVED_ROUTES_DATA = True
ROAD_WIDTH = 10
NUMBER_OF_FAMILIES_IN_A_FLAT = 5

#testing using map data/minecraft_maps/Test 1
VISITS_PER_BUILDING_TYPE = [0, 2, 5, 3, 0, 1] #[HOUSE,RESTAURANT,FACTORY,SHOP,FLATS,TOWN_HALL]

BUILDINGS_IN_VILLAGE = [building_types.TOWN_HALL, building_types.FACTORY, building_types.SHOP
                  , building_types.RESTAURANT, building_types.FLATS, building_types.HOUSE
                  , building_types.HOUSE, building_types.HOUSE, building_types.HOUSE
                  , building_types.HOUSE]

buildingMaps = buildings()
builder = Builder()

#structure = buildingMaps.getRandomByType(building_types.FACTORY)
#structure = buildingMaps.getRandomByTypeAndSize(building_types.SHOP, 25, 22)
#structure = buildingMaps.getBiggestByTypeAndSize(building_types.FACTORY, 15, 25)
#structure = buildingMaps.getRandomBySize(15, 25)
#structure = buildingMaps.getBiggestBySize(15, 25)

#structure = buildingMaps.getByName(building_names.APPLE_STORE)
#builder.create(-6, -246, orientations.EAST, structure)

#map Test 1
#locations = [(-16,-227),(-31,-245),(5,-260),(9,-236),(22,-213),(22,-149),(84,-194),(37,-223),(-26,-270),(-6,-246)]
locations = [(61,-490),(37,-518),(-23,-572),(20,-560),(28,-458),(9,-477),(12,-530),(61,-563),(81,-524),(116,-491)]

structure_names = [building_names.FUTURISTIC_MODERN_HOME_5, building_names.SMALL_MEDIEVAL_HOME_4
                   , building_names.SMALL_MEDIEVAL_HOME_4, building_names.MEDIEVAL_SAWMILL
                   , building_names.STARBUCKS_MODERN, building_names.MEDIEVAL_TOWN_MEDIUM_HOUSE
                   , building_names.SMALL_MODERN_RESTAURANT_2, building_names.MODERN_BOOK_SHOP
                   , building_names.APPLE_STORE, building_names.SMALL_MODERN_RESTAURANT_2]

average_location = (0, 0)
for location in locations:
    average_location = average_location[0] + location[0], average_location[1] + location[1]
average_location = int(average_location[0] / len(locations)), int(average_location[1] / len(locations))

door_locations = []
facing_directions = []

for location in locations:
    if location[0] - average_location[0] > location[1] - average_location[1]:
        if location[0] - average_location[0] < 0 :
            facing_directions.append(orientations.EAST)
        else:
            facing_directions.append(orientations.WEST)
    else:
        if location[1] - average_location[1] < 0 :
            facing_directions.append(orientations.SOUTH)
        else:
            facing_directions.append(orientations.NORTH)
            
#Connect locations.

#Functional sites will be heavily connected by roads. Residential only loosely connected.
#Will assign which are residential/functional site based on manhattan distances to avoid calculating A* from all sites 
#to all sites (too much processing time)

n_sites = len(locations)
house_count = int(n_sites * PERCENTAGE_OF_RESIDENTIAL)
number_of_functional = n_sites - house_count
manhattan_distances = np.zeros( (n_sites, n_sites) )
avoid_rects = []

if DRAW_HOUSES_ON :
    for site1 in range(n_sites):
        structure = buildingMaps.getByName(structure_names[site1])
        success = builder.create(locations[site1][0], locations[site1][1], facing_directions[site1], structure)
        if success:
            door_location = building_site.move_location(builder.last_site().door_location, facing_directions[site1], int((ROAD_WIDTH + 1) / 2))
            door_locations.append(door_location)
            avoid_rects.append(builder.last_site().coords)
        else:
            door_locations.append(locations[site1])
else :
    door_locations = [(61, -501), (37, -528), (-23, -562), (38, -560), (28, -472), (9, -491), (12, -518), (49, -563), (67, -524), (104, -491)]
    avoid_rects = [(56, -495, 66, -485), (34, -522, 40, -515), (-26, -575, -20, -568), (8, -567, 32, -553), (21, -466, 35, -450), (2, -485, 16, -469), (6, -535, 19, -524), (55, -568, 66, -557), (73, -531, 89, -517), (110, -497, 121, -484)]

for site1 in range(n_sites):
    for site2 in range(site1 + 1, n_sites):
        if site1 != site2 :
            manhattan_distances[site1][site2] = abs(door_locations[site1][0] - door_locations[site2][0]) + abs(door_locations[site1][1] - door_locations[site2][1])
            manhattan_distances[site2][site1] = manhattan_distances[site1][site2]

indexes_ordered_total_distances = np.argsort([sum(col) for col in zip(*manhattan_distances)]) 
functional_indices = indexes_ordered_total_distances[:number_of_functional]
house_indices = indexes_ordered_total_distances[number_of_functional:]

print(indexes_ordered_total_distances)

roads = []
roads_addresses = []

#road from every functional to every other functional site

connected_sites = functional_indices[:]
unconnected_sites = house_indices[:]

for site1 in range(n_sites) : # functional_indices:
    for site2 in range(n_sites) : # functional_indices:
        if site1 != site2 :
            if (site1, site2) not in roads and (site2, site1) not in roads:
                roads.append((site1, site2))
                roads_addresses.append((door_locations[site1], door_locations[site2]))

#while unconnected_sites:
#    min_distance = sys.maxsize
#    win_index = -1
#    for unconnected in unconnected_sites:
#        for connected in connected_sites:
#            if min_distance < manhattan_distances :

if USE_SAVED_ROUTES_DATA :
    roads_routes = existing_roads_routes
else:
    roads_routes = find_routes(roads_addresses, 15, 3, avoid_rects)

start_bfs = time.time()


distances = {}

actual_distances = np.zeros( (n_sites, n_sites) )

for roads_route in roads_routes:
    if (roads_route[0][0], roads_route[0][2]) not in door_locations or (roads_route[-1][0], roads_route[-1][2]) not in door_locations:
        raise err("Incomplete route!?")
    ind1 = door_locations.index((roads_route[0][0], roads_route[0][2]))
    ind2 = door_locations.index((roads_route[-1][0], roads_route[-1][2]))
    actual_distances[ind1][ind2] = len(roads_route)
    actual_distances[ind2][ind1] = len(roads_route)

locations_availble = list(range(len(BUILDINGS_IN_VILLAGE)))

buildings_available_no_houses = list(filter(lambda x: x != building_types.HOUSE, BUILDINGS_IN_VILLAGE))
no_of_houses = len(BUILDINGS_IN_VILLAGE) - len(buildings_available_no_houses)

chosen_house_locations = []

class attempt_details():
    def __init__(self, parent, location_index: int, building: building_types, is_top_node: bool = False):
        self.parent = parent
        self.location_index = location_index
        self.building = building
        self.is_top_node = is_top_node

    @classmethod
    def get_top_node(cls):
        return cls(None, -1, building_types.UNKNOWN, True)

#find places for houses.  This is done first so that the following is not considered separately:
#{HouseA in Location1, HouseB in Location2} and {HouseB in Location1, HouseA in Location2}
#Step1 does not distinguish between HouseA and HouseB and so saves processing time
#If only bfs_step2 was used, this would be considered separately
def recursive_bfs_step1(  attempt: attempt_details
                        , house_count: int
                        , locations_list : List[int]) -> Tuple[int, List[Tuple[int, building_types]]]:
    if house_count == 0 :
        return recursive_bfs_step2(attempt, buildings_available_no_houses, locations_list)

    winning_score = sys.maxsize
    available_locations = len(locations_list) - house_count + 1

    for i in range(available_locations) :
        if house_count == no_of_houses :
            mins, sec = divmod(time.time() - start_bfs, 60)
            print(f"Find optimum location {100*i/available_locations:.0f}% complete  {mins:.0f}m {sec:.0f}s Winning score: {winning_score}")

        location = locations_list.pop(i)

        candidate_score, candidate_building_locations = recursive_bfs_step1(
              attempt_details(attempt, location, building_types.HOUSE), house_count - 1, locations_list)

        locations_list.insert(i, location)

        if candidate_score < winning_score :
            winning_score = candidate_score
            winning_building_locations = candidate_building_locations

    return winning_score, winning_building_locations


def recursive_bfs_step2(     attempt: attempt_details
                           , buildings_list : List[building_types]
                           , locations_list : List[int]) -> Tuple[int, List[Tuple[int, building_types]]]:

    if len(locations_list) == 0 :
        
        function_building_locations = []
        house_location_adresses = []
        building_locations = []
        while not attempt.is_top_node:
            building_locations.append((attempt.location_index, attempt.building))
            if attempt.building == building_types.HOUSE :
                house_location_adresses.append(attempt.location_index)
            elif attempt.building == building_types.FLATS :
                flat_address = attempt.location_index
            else:
                function_building_locations.append((attempt.location_index, attempt.building))
            attempt = attempt.parent

        total_distance = 0
        for candidate_address, candidate_building in function_building_locations:
            visit_count = VISITS_PER_BUILDING_TYPE[candidate_building.value]
            
            for house_address in house_location_adresses:
                total_distance += visit_count * actual_distances[candidate_address][house_address]
            total_distance += visit_count * NUMBER_OF_FAMILIES_IN_A_FLAT * actual_distances[candidate_address][flat_address]

        return total_distance, building_locations

    winning_score = sys.maxsize
    winning_building_locations = []

    location = locations_list.pop(0)

    for i in range(len(buildings_list)):

        building = buildings_list.pop(i)

        candidate_score, candidate_building_locations = recursive_bfs_step2(
              attempt_details(attempt, location, building), buildings_list, locations_list)

        buildings_list.insert(1, building)

        if candidate_score < winning_score :
            winning_score = candidate_score
            winning_building_locations = candidate_building_locations

    locations_list.insert(0, location)

    return winning_score, winning_building_locations

total_distance, building_locations = recursive_bfs_step1(attempt_details.get_top_node(), no_of_houses, locations_availble)

print(f"Total distance: {total_distance}")
print(f"Building locations: {building_locations}")

mins, sec = divmod(time.time() - start_bfs, 60)
print(f"/n/nTotal Time elapsed BFS: {mins:.0f}m {sec:.0f}s")

a=2

#for road in roads:
#    roads_routes.append(find_route(locations[road[0]], locations[road[1]]))

print("Complete")


#for i in range(1, 5):
#    structure = buildingMaps.getRandomBySize(15, 25)
#    if not builder.create_adjacent_to_last(orientations.SOUTH, 1, orientations.EAST, structure):
#        break

#x = 300
#for z in range(45, 130, 15) :
#    structure = buildings.getRandomBySize(15, 25)
#    builder = Builder(x, z, orientations.EAST, structure)

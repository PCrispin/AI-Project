from math import sqrt
from random import *
from numpy import *
from vendor.gdmc_http_client.worldLoader import WorldSlice
from vendor.gdmc_http_client.interfaceUtils import placeBlockBatched, sendBlocks, runCommand
from classes.ENUMS.block_codes import block_codes
from classes.Bool_map import bool_map
from classes.Building_site import building_site
from typing import List, Tuple
import time

MAX_HEIGHT = 255
MIN_HEIGHT = 0
A_BIG_NUMBER = 1000000
BLOCK_BATCH_SIZE = 1000
SQUARE_COST = 2
ENCOURAGE_PENALTY = 1.1
PROXIMITY_PENALTY = 2
SNAP_TO_GRID_PENALTY = 0.2
MAX_HEIGHT_DROP = 1
materials_not_passable = [block_codes.WATER, block_codes.FLOWING_WATER]

materials_vegetation = [  "minecraft:grass"
                        , "minecraft:dandelion"
                        , "minecraft:poppy"
                        , "minecraft:blue_orchid"
                        , "minecraft:allium"
                        , "minecraft:azure_bluet"
                        , "minecraft:red_tulip"
                        , "minecraft:orange_tulip"
                        , "minecraft:white_tulip"
                        , "minecraft:pink_tulip"
                        , "minecraft:oxeye_daisy"
                        , "minecraft:brown_mushroom"
                        , "minecraft:red_mushroom"  ]

MAX_DEPTH = 1000
MAX_DETOUR = 110

#direction_choices = [  [(0, 1), (-2, 1), (-1,1), (1,1), (2,1)]
#                    , [(0, -1), (-2, -1), (-1,-1), (1,-1), (2,-1)]
#                    , [(1, 0), (1, -2), (1, -1), (1,1), (1, 2)]
#                    , [(-1, 0), (-1, -2), (-1, -1), (-1,1), (-1, 2)] ]
#change_direction_matrix = [[(-1,-1), (-1, 1), (-1, 2), (-2, 1)]
#                            , [(1,-1), (-1, -1), (-2, -1), (-1, -2)]
#                            , [(1, 1), (1, -1), (1, -2), (2, -1)]
#                            , [(-1, 1), (1, 1), (2, 1), (1, 2)] ] #checks the diagonals

#road width of 3
direction_choices = [  [(0, 1), (-1,1), (1,1)]
                    , [(0, -1), (-1,-1), (1,-1)]
                    , [(1, 0), (1, -1), (1,1)]
                    , [(-1, 0), (-1, -1), (-1,1)] ]
change_direction_matrix = [[(-1,-1), (-1, 1)]
                            , [(1,-1), (-1, -1)]
                            , [(1, 1), (1, -1)]
                            , [(-1, 1), (1, 1)] ] #checks the diagonals

coloured_blocks = [ "minecraft:white_terracotta"
                    , "minecraft:orange_terracotta"
                    , "minecraft:magenta_terracotta"
                    , "minecraft:light_blue_terracotta"
                    , "minecraft:yellow_terracotta"
                    , "minecraft:lime_terracotta"
                    , "minecraft:pink_terracotta"
                    , "minecraft:gray_terracotta"
                    , "minecraft:light_gray_terracotta"
                    , "minecraft:cyan_terracotta"
                    , "minecraft:purple_terracotta"
                    , "minecraft:blue_terracotta"
                    , "minecraft:brown_terracotta"
                    , "minecraft:green_terracotta"
                    , "minecraft:red_terracotta"
                    , "minecraft:black_terracotta"]

def find_routes(roads : List[Tuple[Tuple[int, int], Tuple[int, int]]]
                , grid_width: int, margin_width: int
                , avoid_rects: List[Tuple[int, int, int, int]]) -> List[List[Tuple[int,int,int]]]:
    start = time.time()
    
    areas_min_x, areas_min_z = A_BIG_NUMBER, A_BIG_NUMBER
    areas_max_x, areas_max_z = -A_BIG_NUMBER, -A_BIG_NUMBER

    for road in roads:
        areas_min_x, areas_min_z = min(areas_min_x, road[0][0], road[1][0]), min(areas_min_z, road[0][1], road[1][1])
        areas_max_x, areas_max_z = max(areas_max_x, road[0][0], road[1][0]), max(areas_max_z, road[0][1], road[1][1])

    areas = (areas_min_x - MAX_DETOUR, areas_min_z - MAX_DETOUR
             , areas_max_x - areas_min_x + 2 * MAX_DETOUR
             , areas_max_z - areas_min_z + 2 * MAX_DETOUR)

    world_slice = WorldSlice(areas)
    world_map = bool_map(areas, avoid_rects, margin_width, world_slice)

    roads_routes = []

    count = 0
    for road in roads:
        start_road = time.time()
        roads_routes.append(_find_route(road[0], road[1], world_slice, world_map, grid_width))
        mins, sec = divmod(time.time() - start_road, 60)
        mins2, sec2 = divmod(time.time() - start, 60)
        count += 1
        print(f"Time elapsed searching for {count}/{len(roads)} road: {mins:.0f}m {sec:.0f}s accum: {mins2:.0f}m {sec2:.0f}s")

    index = 0
    for route in roads_routes:
        for brick in route:
            placeBlockBatched(brick[0], brick[1], brick[2], coloured_blocks[index % len(coloured_blocks)], BLOCK_BATCH_SIZE)
        index += 1
    sendBlocks()

    mins, sec = divmod(time.time() - start, 60)
    print(f"/n/nTotal Time elapsed searching {len(roads)} road: {mins:.0f}m {sec:.0f}s")

    return roads_routes

def _find_route(origin: Tuple[int, int], destination: Tuple[int, int], world_slice: WorldSlice
                     , world_map: bool_map, grid_width: int) -> List[Tuple[int,int]]:

    area_min_x, area_min_z = min(origin[0], destination[0]) - MAX_DETOUR, min(origin[1], destination[1]) - MAX_DETOUR
    area_max_x, area_max_z = max(origin[0], destination[0]) + MAX_DETOUR, max(origin[1], destination[1]) + MAX_DETOUR

    def findHeight(x: int, z: int) -> Tuple[int, int]:
        wX, wZ = x - world_slice.rect[0], z - world_slice.rect[1]
        if 0 <= wX < world_slice.rect[2] and 0 <= wZ < world_slice.rect[3] :
            y = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][wX][wZ]
            material = world_slice.getBlockAt((x, y-1, z))

            while material in materials_vegetation:
                y -= 1
                material = world_slice.getBlockAt((x, y-1, z))

            return y, material
        else:
            return MAX_HEIGHT, block_codes.AIR

    destination_y, desintation_material = findHeight(destination[0], destination[1])
    origin_y, origin_material = findHeight(origin[0], origin[1])
    tile_map = {}
    frontier = []            
    route = []
    manhattan = abs(origin[0] - destination[0]) + abs(origin[1] - destination[1])

    def get_tile(x: int, y: int, z: int, cost: int, from_tile: Tuple[int,int], depth: int, is_origin: bool = False) -> Tuple[int, int, int, Tuple[int, int], bool, int]:
        heuristic =  abs(destination[0] - x) + abs(destination[1] - z) + (destination_y - y)
        return (cost, heuristic, cost + heuristic, from_tile, is_origin, depth, y)
        #cost=0 heuristic=1 total=2 from_tile=3 is_origin=4 depth=5 y=6

    def replace_tile(cost: int, heuristic: int, y: int, from_tile: Tuple[int,int], depth: int) -> Tuple[int, int, int, Tuple[int, int], bool, int]:
        return (cost, heuristic, cost + heuristic, from_tile, False, depth, y)
        #cost=0 heuristic=1 total=2 from_tile=3 is_origin=4 depth=5 y=6

    focus_tile = get_tile(origin[0], origin_y, origin[1], 0, (origin[0], origin[1]), 0, True)
    tile_map[origin[0], origin[1]] = focus_tile
    
    def frontier_update(x: int, z: int, tile: Tuple[int, int, int, Tuple[int, int], bool, int]):
        matches = [item for item in frontier if item[0] == x and item[1] == z]

        if len(matches) > 0:
            frontier.remove(matches[0])
        frontier.append((x, z, tile[2], tile[1])) #total=2  heuristic=1 

    frontier_update(origin[0], origin[1], focus_tile) 

    print("\nFinding route: [{}, {}] to [{}, {}]   dx:{} dz:{} dy:{} ".format(origin[0], origin[1], destination[0], destination[1], destination[0] - origin[0], destination[1] - origin[1], destination_y - origin_y))

    #for tz in range (-550, -530):
    #    s = ''
    #    for tx in range (-10,10):
    #        if world_slice.heightmaps['OCEAN_FLOOR'][tx-world_slice.rect[0]][tz-world_slice.rect[1]] == world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][tx-world_slice.rect[0]][tz-world_slice.rect[1]] :
    #            s = s + '0'
    #        else:
    #            s = s + '1'
    #    print(s)

    spread = []
    h= abs((grid_width - 1) / 2)
    for k in range(grid_width):
        spread.append(1 + SNAP_TO_GRID_PENALTY * (h - abs(h - k % grid_width))) # will look like (1, 1.2, 1.4, 1.2, 1) for 5

    def set_route(focus_x: int, focus_z: int, focus_tile: Tuple[int, int, int, Tuple[int, int], bool, int], depth: int):
        while not(focus_tile[4]):                   #4=is_origin
            route.append((focus_x, focus_tile[6], focus_z)) #y=6
            focus_x, focus_z = focus_tile[3]        #3=from_tile
            focus_tile = tile_map[focus_x, focus_z]
        route.append((origin[0], origin_y, origin[1]))
        world_map.set_road(route, destination)
        print(f"Route found length:{depth} manhattan dist: {manhattan} considered: {len(tile_map)}")

    while frontier:
        frontier.sort(key=lambda x: (x[2], x[3]), reverse=False)            #frontier[ total=2 heuristic=3 ]

        focus_x, focus_z, focus_total, focus_heuristic = frontier.pop(0)
        focus_tile = tile_map[focus_x, focus_z]

        if focus_tile[5] >= MAX_DEPTH :         #5=depth
            print("Max depth reached")
            return []

        #if path to destination is found, find the entire route and exit search
        if focus_x == destination[0] and focus_z == destination[1]:
            set_route(focus_x, focus_z, focus_tile, focus_tile[5])    #depth=5
            return route

        #print("****************************\n{}\nRelative to origin: [{}, {}]-y:{}\n{} tiles considered so far".format(str(focus_tile), origin[0] - focus_tile.x, origin[1] - focus_tile.z, y_start - focus_tile.y, len(tile_map)))
        #for t in frontier :
        #    print(str(t))

        for direction_values in direction_choices:
            new_x = focus_x + direction_values[0][0]
            new_z = focus_z + direction_values[0][1]

            if area_min_x <= new_x < area_max_x and area_min_z <= new_z < area_max_z :

                has_road, road_already_goes_to_destination, existing_route = world_map.check_already_goes_to(new_x, new_z, destination)
                if road_already_goes_to_destination :
                    depth = focus_tile[5] + len(route)        #5=depth
                    print(f"Partial route taken from existing road {origin}-{destination} - borrowed route length: {len(existing_route)}")
                    for address in existing_route:
                        route.append(address)
                    set_route(focus_x, focus_z, focus_tile, depth)
                    return route

                factor = spread[new_x % grid_width] * spread[new_z % grid_width] #snap to grid
                if not has_road :
                    factor *= ENCOURAGE_PENALTY
                if world_map.get_penalty_value(new_x, new_z):
                    factor *= PROXIMITY_PENALTY

                new_cost = focus_tile[0] + SQUARE_COST * factor     #0=cost

                #Get tile information from memory or create
                if (new_x, new_z) in tile_map :
                    existing_tile = tile_map[new_x, new_z]
                    new_cost += abs(existing_tile[6] - focus_tile[6]) * SQUARE_COST   #y=6

                    if existing_tile[0] <= new_cost :       #0=cost
                        continue

                    new_tile = replace_tile(new_cost, existing_tile[1], existing_tile[6], (focus_x, focus_z), focus_tile[5] + 1) #heuristic=1 depth=5 y=6
                else :
                    if world_map.get_avoid_value(new_x, new_z) :
                        continue

                    new_y, new_material = findHeight(new_x, new_z)

                    if abs(new_y - focus_tile[6]) > MAX_HEIGHT_DROP :   #y=6
                        continue

                    new_cost += abs(new_y - focus_tile[6]) * SQUARE_COST  #y=6
                    new_tile = get_tile(new_x, new_y, new_z, new_cost, (focus_x, focus_z), focus_tile[5] + 1)   #depth=5
                
                tile_map[new_x, new_z] = new_tile               
                frontier_update(new_x, new_z, new_tile) #total=2  heuristic=1 

    print("No route possible!")
    return []





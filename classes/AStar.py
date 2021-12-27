from math import sqrt
from random import *
import time
from sys import maxsize 
from typing import List, Tuple
from vendor.gdmc_http_client.worldLoader import WorldSlice
from vendor.gdmc_http_client.interfaceUtils import placeBlockBatched, sendBlocks, runCommand, setBlock
from constants import MAX_DETOUR, DEBUG_DRAW_WORKINGS, BLOCK_BATCH_SIZE
from classes.ENUMS.block_codes import block_codes
from classes.Bool_map import bool_map
from classes.Building_site import building_site

MAX_HEIGHT: int = 255
MIN_HEIGHT: int = 0
A_BIG_NUMBER: int = 1000000
ENCOURAGE_PENALTY:float = 0.5
MAX_SNAP_TO_GRID_PENALTY:float = 2
NEAR_OBSTACLE_PENALTY:float = 1

THRESHOLD_GAIN_FOR_REENTRY_TO_FRONTIER = 2

LAMP_POST_SPACING = 10
STRIPE_SPACING = 10



MAX_HEIGHT_DROP:int = 1
MAX_DEPTH:int = 1000

materials_vegetation:List[str] = [    "minecraft:grass"
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

direction_choices = [ (0, 1) , (0, -1) , (1, 0)  , (-1, 0)  ]

def create_roads( roads : List[Tuple[Tuple[int, int], Tuple[int, int]]]
                , grid_width, door_locations: List[Tuple[int, int]]
                , world_map: bool_map, world_slice: WorldSlice) -> List[List[int]]:
    start = time.time()

    roads_routes = []

    lamp_posts = []
    lamp_post_spacing_squared = LAMP_POST_SPACING ** 2

    count = 0
    no_route_found_count = {}

    for road in roads:
        start_road = time.time()
        if road[0] not in no_route_found_count or no_route_found_count[road[0]] < 2 :
            road_route = _find_route(road[0], road[1], world_slice, world_map, grid_width)

            if len(road_route) == 0:
                no_route_found_count[road[0]] = 1 if road[0] not in no_route_found_count else no_route_found_count[road[0]] + 1
                no_route_found_count[road[1]] = 1 if road[1] not in no_route_found_count else no_route_found_count[road[1]] + 1
        else:
            road_route = []

        roads_routes.append(road_route)

        mins, sec = divmod(time.time() - start_road, 60)
        mins2, sec2 = divmod(time.time() - start, 60)
        count += 1
        print(f"Time elapsed searching for {count}/{len(roads)} road: {mins:.0f}m {sec:.0f}s accum: {mins2:.0f}m {sec2:.0f}s")

    def draw_road(x: int, y_plus_1:int, z: int, is_stripe: bool = False) :
        if not world_map.get_avoid_value(x, z) :
            if is_stripe :
                placeBlockBatched(x, y_plus_1 - 1, z, block_codes.BLACK_TERRACOTTA.value, BLOCK_BATCH_SIZE)
            else :
                placeBlockBatched(x, y_plus_1 - 1, z, block_codes.BLACK_TERRACOTTA.value, BLOCK_BATCH_SIZE)

    def draw_lamp_post(x: int, y:int, z: int) :
        for lamp_post in lamp_posts :
            if (lamp_post[0] - x) ** 2 + (lamp_post[1] - z) ** 2 < lamp_post_spacing_squared :
                return
        lamp_posts.append((x, z))

        if not world_map.get_avoid_value(x, z) :
            placeBlockBatched(x, y + 0, z, block_codes.IRON_BARS.value, BLOCK_BATCH_SIZE)
            placeBlockBatched(x, y + 1, z, block_codes.IRON_BARS.value, BLOCK_BATCH_SIZE)
            placeBlockBatched(x, y + 2, z, block_codes.IRON_BARS.value, BLOCK_BATCH_SIZE)
            placeBlockBatched(x, y + 3, z, block_codes.IRON_BARS.value, BLOCK_BATCH_SIZE)
            placeBlockBatched(x, y + 4, z, block_codes.TORCH.value, BLOCK_BATCH_SIZE)

    for route in roads_routes:
        route_length = len(route)
        
        if route_length > 1 :
            continuous_e_w_distance = 0
            continuous_n_s_distance = 0
            for index in range(route_length + 1):
                if index == route_length :
                    #So that adjacent bricks next to last brick in the path are drawn.
                    brick_x, brick_y, brick_z = route[-2] 
                    previous_brick_x, previous_brick_y, previous_brick_z = route[-1] 
                elif index == 0 :
                    #So the first brick is drawn
                    brick_x, brick_y, brick_z = route[0] 
                    previous_brick_x, previous_brick_y, previous_brick_z = route[1] 
                else:
                    brick_x, brick_y, brick_z = route[index] 
                    previous_brick_x, previous_brick_y, previous_brick_z = route[index-1] 
                
                if brick_x - previous_brick_x == 0 :
                    continuous_e_w_distance += 1
                    continuous_n_s_distance = 0
                    if index % 10 == 0 :
                        draw_lamp_post(previous_brick_x - 2, previous_brick_y, previous_brick_z)
                    draw_road(previous_brick_x - 1, previous_brick_y, previous_brick_z)
                    draw_road(previous_brick_x + 1, previous_brick_y, previous_brick_z)
                    draw_road(brick_x, brick_y, brick_z, True if continuous_e_w_distance % STRIPE_SPACING == 0 else False)
                else :
                    continuous_e_w_distance = 0
                    continuous_n_s_distance += 1
                    if index % 10 == 0 :
                        draw_lamp_post(previous_brick_x, previous_brick_y, previous_brick_z - 2)
                    draw_road(previous_brick_x, previous_brick_y, previous_brick_z - 1)
                    draw_road(previous_brick_x, previous_brick_y, previous_brick_z + 1)
                    draw_road(brick_x, brick_y, brick_z, True if continuous_n_s_distance % STRIPE_SPACING == 0 else False)

        sendBlocks()

    distances = [[0 for i in range(len(door_locations))] for i in range(len(door_locations))]

    for route in roads_routes:
        if len(route) > 0:
            ind1 = door_locations.index((route[0][0], route[0][2]))
            ind2 = door_locations.index((route[-1][0], route[-1][2]))
            distances[ind1][ind2] = len(route)
            distances[ind2][ind1] = len(route)

    mins, sec = divmod(time.time() - start, 60)
    print(f"\n\nTotal Time elapsed searching {len(roads)} road: {mins:.0f}m {sec:.0f}s")

    return distances

def _find_route(origin: Tuple[int, int], destination: Tuple[int, int], world_slice: WorldSlice
                     , world_map: bool_map, grid_width: int) -> List[Tuple[int,int]]:

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

    destination_x, destination_z = destination[0], destination[1]
    destination_y, desintation_material = findHeight(destination_x, destination_z)
    origin_x, origin_z = origin[0], origin[1]
    origin_y, origin_material = findHeight(origin_x, origin_z)

    area_min_x, area_min_z = min(origin_x, destination_x) - MAX_DETOUR, min(origin_z, destination_z) - MAX_DETOUR
    area_max_x, area_max_z = max(origin_x, destination_x) + MAX_DETOUR, max(origin_z, destination_z) + MAX_DETOUR

    if DEBUG_DRAW_WORKINGS : 
        for i in range(2, 10) :
            setBlock(origin_x, origin_y + i, origin_z, block_codes.IRON_BARS.value)
            setBlock(destination_x, destination_y + i, destination_z, block_codes.IRON_BARS.value)
        setBlock(origin_x, origin_y + 10, origin_z, block_codes.TORCH.value)
        setBlock(destination_x, destination_y + 10, destination_z, block_codes.TORCH.value)

    def finish_up(route: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
        if DEBUG_DRAW_WORKINGS : 
            for i in range(2, 11) :
                setBlock(origin_x, origin_y + i, origin_z, block_codes.AIR.value)
                setBlock(destination_x, destination_y + i, destination_z, block_codes.AIR.value)
        return route

    if world_map.get_avoid_value(destination_x, destination_z) :
        print("Route not possible.  Destination is in water or at building location!")
        return finish_up([])

    if world_map.get_avoid_value(origin_x, origin_z) :
        print("Route not possible.  Origin is in water or at building location!")
        return finish_up([])

    tile_map = {}   #only change in tile_bfs
    frontier = []   #only change in tile_bfs           
    route = []
    manhattan = abs(origin_x - destination_x) + abs(origin_z - destination_z)

    spread = []
    h= abs((grid_width - 1) / 2)
    for k in range(grid_width):
        spread.append(MAX_SNAP_TO_GRID_PENALTY * min(k,-k % grid_width) / (2 * h)) 
    # spread for 15: [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.2, 2.0, 1.8, 1.6, 1.4, 1.2, 1.0]

    def get_snap_to_grid_penalty(x: int, z: int) -> float:
        return spread[x % grid_width] + spread[z % grid_width]

    class tile_bfs():
        def __init__(self, x: int, y: int, z: int, cost: int, from_tile: 'tile_bfs', depth: int):
            self.x: int = x
            self.y: int = y
            self.z: int = z
            self.from_tile = from_tile
            self.depth: int = depth
            self.is_origin: bool = False

            self._set_cost(cost)

            tile_map[self.x, self.z] = self
            frontier.append(self)           
            self.is_in_frontier = True

        def _set_cost(self, cost: int):
            self.cost: int = cost
            self.heuristic =  abs(destination_x - self.x) + abs(destination_z - self.z) #+ (destination_y - y)
            self.total = self.heuristic + self.cost

        def update(self, new_cost: int, from_tile: 'tile_bfs'):
            self.from_tile = from_tile
            self.depth: int = from_tile.depth + 1
            self._set_cost(new_cost)

            if not self.is_in_frontier :
                frontier.append(self)           

        def already_in_route(self, x: int, z: int) -> bool :
            current = self
            while True:
                if current.is_origin :
                    return False
                if current.x == x and current.z == z :
                    return True
                current = current.from_tile

        @classmethod
        def get_root_node(cls, x: int, y: int, z: int) -> 'tile_bfs' :
            a = cls(x, y, z, 0, None, 0)
            a.is_origin = True
            return a

        @classmethod
        def frontier_pop(cls) -> 'tile_bfs' :
            min_total :int = maxsize
            min_heuristic :int = maxsize
            min_i: int = -1

            for i in range(len(frontier)):
                if frontier[i].total < min_total and frontier[i].heuristic < min_heuristic :
                    min_i = i
                    min_total = frontier[i].total
                    min_heuristic = frontier[i].heuristic

            lowest_tile_bfs = frontier.pop(min_i)
            lowest_tile_bfs.is_in_frontier = False

            #lowest_tile_bfs: tile_bfs = min(frontier,key=attrgetter('number'))
            #frontier.sort(key=lambda x: (x., x[3]), reverse=False)            #frontier[ total=2 heuristic=3 ]
            #lowest_tile_bfs = frontier.pop(0)
            #lowest_tile_bfs.is_in_frontier = False

            return lowest_tile_bfs

    focus_tile = tile_bfs.get_root_node(origin_x, origin_y, origin_z)

    print("\nFinding route: [{}, {}] to [{}, {}]   dx:{} dz:{} dy:{} ".format(origin_x, origin_z, destination_x, destination_z, destination_x - origin_x, destination_z - origin_z, destination_y - origin_y))

    def set_route(focus_tile: tile_bfs, depth: int):
        while True:                   
            route.append((focus_tile.x, focus_tile.y, focus_tile.z)) 
            if focus_tile.is_origin :
                break
            focus_tile: tile_bfs = focus_tile.from_tile

        world_map.set_road(route, destination)
        print(f"Route found length:{depth} manhattan dist: {manhattan} considered: {len(tile_map)}")

    while frontier:
        focus_tile: tile_bfs = tile_bfs.frontier_pop()

        if DEBUG_DRAW_WORKINGS : 
            if world_slice.getBlockAt((focus_tile.x, focus_tile.y - 1, focus_tile.z)) != block_codes.YELLOW_TERRACOTTA.value :
                setBlock(focus_tile.x, focus_tile.y - 1, focus_tile.z, block_codes.YELLOW_TERRACOTTA.value) 
            else :
                setBlock(focus_tile.x, focus_tile.y - 1, focus_tile.z, block_codes.ORANGE_TERRACOTTA.value) 
            print(f"Focus tile: [{focus_tile.x:.0f}, {focus_tile.y:.0f}, {focus_tile.z:.0f}] total: {focus_tile.total:.0f}")

        if focus_tile.depth >= MAX_DEPTH :         
            print("Max depth reached")
            return finish_up([])

        #if path to destination is found, find the entire route and exit search
        if focus_tile.x == destination_x and focus_tile.z == destination_z:
            set_route(focus_tile, focus_tile.depth)    
            return finish_up(route)

        for direction_values in direction_choices:
            new_x, new_z = focus_tile.x + direction_values[0], focus_tile.z + direction_values[1]

            if area_min_x <= new_x < area_max_x and area_min_z <= new_z < area_max_z :

                has_road, road_already_goes_to_destination, existing_route = world_map.check_already_goes_to(new_x, new_z, destination)

                if road_already_goes_to_destination :
                    depth = focus_tile.depth + len(route)        
                    print(f"Partial route taken from existing road {existing_route[-1]}-{existing_route[0]} - borrowed route length: {len(existing_route)}")
                    for address in existing_route:
                        route.append(address)
                    set_route(focus_tile, depth)
                    return finish_up(route)

                new_cost = focus_tile.cost + 1 \
                        + (NEAR_OBSTACLE_PENALTY if world_map.get_is_near_obstacle(new_x, new_z) else 0) \
                        + get_snap_to_grid_penalty(new_x, new_z) \
                        + (0 if has_road else ENCOURAGE_PENALTY)

                #Get tile information from memory or create
                if (new_x, new_z) in tile_map :
                    existing_tile : tile_bfs = tile_map[new_x, new_z]

                    if (existing_tile.is_in_frontier and existing_tile.cost > new_cost) \
                            or existing_tile.cost - new_cost > THRESHOLD_GAIN_FOR_REENTRY_TO_FRONTIER :    

                        existing_tile.update(new_cost, focus_tile)
                else :
                    if world_map.get_avoid_value(new_x, new_z) :
                        if DEBUG_DRAW_WORKINGS : 
                            new_y, new_material = findHeight(new_x, new_z)
                            if world_map.get_avoid_water_value(new_x, new_z) :
                                setBlock(new_x, new_y - 1, new_z, block_codes.BLACK_TERRACOTTA.value) 
                                print(f"AVOID WATER BLOCKED: [{focus_tile.x:.0f}, {new_y:.0f}, {focus_tile.z:.0f}] {new_material}")
                            else :
                                setBlock(new_x, new_y - 1, new_z, block_codes.BLACK_TERRACOTTA.value) 
                                print(f"AVOID BUILDING BLOCKED: [{focus_tile.x:.0f}, {new_y:.0f}, {focus_tile.z:.0f}] {new_material}")
                    else:
                        new_y, new_material = findHeight(new_x, new_z)

                        if abs(new_y - focus_tile.y) > MAX_HEIGHT_DROP :   
                            if DEBUG_DRAW_WORKINGS : 
                                setBlock(new_x, new_y - 1, new_z, block_codes.GRAY_TERRACOTTA.value) 
                                print(f"TOO TALL BLOCKED: [{focus_tile.x:.0f}, {new_y:.0f}, {focus_tile.z:.0f}] {new_material}")
                        else :
                            if DEBUG_DRAW_WORKINGS : 
                                setBlock(new_x, new_y - 1, new_z, block_codes.LIGHT_BLUE_TERRACOTTA.value) 
                                print(f"Add to frontier: [{focus_tile.x:.0f}, {new_y:.0f}, {focus_tile.z:.0f}] {new_material} {new_cost:.2f}")

                            new_tile = tile_bfs(new_x, new_y, new_z, new_cost, focus_tile, focus_tile.depth + 1)   

    print(f"No route possible! Tried {len(tile_map)} blocks.")
    return finish_up([])


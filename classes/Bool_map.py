from vendor.gdmc_http_client.worldLoader import WorldSlice
from typing import List, Tuple

class bool_map():
    class tile_info():
        def __init__(self):
            self.avoid = False
            self.penalty = False
            self.has_road = False
            self.already_goes_to = {}

    def __init__(self, areas: Tuple[int, int, int, int], avoid_rects: List[Tuple[int,int,int,int]], margin: int, world_slice: WorldSlice):
        """description of class"""
        self.minX = areas[0]
        self.minZ = areas[1]
        self.width = areas[2]
        self.depth = areas[3]

        self.matrix = [ [ self.tile_info() for j in range(self.depth) ] for i in range(self.width) ]

        self.route_list = []

        for rect in avoid_rects:
            for i in range(rect[0] - self.minX, rect[2] - self.minX + 1):
                for j in range(rect[1] - self.minZ, rect[3] - self.minZ + 1):
                    if 0 <= i < self.width and 0 <= j < self.depth :
                        self.matrix[i][j].avoid = True

        #TODO: only loop through intersection of matrix and world_slice
        sea_floor = world_slice.heightmaps['OCEAN_FLOOR']
        surface = world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']

        for i in range(world_slice.rect[2]):
            for j in range(world_slice.rect[3]):
                if sea_floor[i][j] < surface[i][j] :
                    j_m = world_slice.rect[1] + j - self.minZ
                    i_m = world_slice.rect[0] + i - self.minX
                    if 0 <= i_m < self.width and 0 <= j_m < self.depth :
                        self.matrix[i_m][j_m].avoid = True

        changes = []
        for i in range(margin, self.width - margin):
            for j in range(margin, self.depth - margin):
                if not self.matrix[i][j].avoid :
                    for k in range(1, margin + 1):
                        if self.matrix[i-k][j].avoid :
                            changes.append((i,j))
                            break
                        elif self.matrix[i][j-k].avoid :
                            changes.append((i,j))
                            break
                        if self.matrix[i+k][j].avoid :
                            changes.append((i,j))
                            break
                        elif self.matrix[i][j+k].avoid :
                            changes.append((i,j))
                            break
        for change in changes:
            self.matrix[change[0]][change[1]].penalty = True

    def get_avoid_value(self, x: int, z: int) -> bool:
        return self.matrix[x - self.minX][z - self.minZ].avoid

    def get_penalty_value(self, x: int, z: int) -> bool:
        return self.matrix[x - self.minX][z - self.minZ].penalty

    def get_has_road_value(self, x: int, z: int) -> bool:
        return self.matrix[x - self.minX][z - self.minZ].has_road

    def set_road(self, coords: List[Tuple[int, int, int]], goes_to: Tuple[int, int]):
        route_index = len(self.route_list)
        self.route_list.append(coords)

        for coord in coords:
            current_tile = self.matrix[coord[0] - self.minX][coord[2] - self.minZ]
            current_tile.has_road = True
            current_tile.already_goes_to[goes_to] = route_index

    def check_already_goes_to(self, x: int, z: int, goes_to: Tuple[int, int]) -> Tuple[bool, bool, List[Tuple[int, int, int]]] :
        current_tile = self.matrix[x - self.minX][z - self.minZ]

        if current_tile.has_road and goes_to in current_tile.already_goes_to :
            has_road = True
            route = self.route_list[current_tile.already_goes_to[goes_to]]

            current_address = (x, z)
            for index in range(len(route)) :
                if x == route[index][0] and z == route[index][2] :
                    return has_road, True, route[0:index+1]
        else :
            has_road = False
        return has_road, False, None

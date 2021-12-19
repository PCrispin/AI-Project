from classes.ENUMS.orientations import orientations
from classes.Building import building
from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_names import building_names
from typing import Tuple

class building_site(object):
    AREA_EXPANDED_MARGIN = 5

    """Specifics of a building instance"""
    x_center = 0
    z_center = 0
    y_min = 0

    coords = (0,0,0,0)
    area_expanded = (0,0,0,0)

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

    repeaterXs = []
    repeaterZs = []

    building_map_x_index = 0
    building_map_z_index = 2

    def __init__(self, building: building, x_center: int, z_center: int, orientation: orientations, required_width: int = 0, required_depth: int = 0):
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
            self.repeaterXs, self.repeaterZs = building.getRepeaters(required_width, required_depth)
            building_map_x_index = 0
            building_map_z_index = 2
        else:
            self.raw_x_length = building.depth
            self.raw_z_length = building.width
            self.repeaterZs, self.repeaterXs = building.getRepeaters(required_width, required_depth)
            self.building_map_x_index = 2
            self.building_map_z_index = 0

        self.final_x_length = self.raw_x_length + len(self.repeaterXs) - 1
        self.final_z_length = self.raw_z_length + len(self.repeaterZs) - 1

        self.x_factor, self.z_factor = ((-1, 1), (-1, -1), (1, -1), (1, 1))[orientation.value] #w,n,e,s

        self.x_zero = x_center + (-1 * self.x_factor * int(self.final_x_length / 2))
        self.z_zero = z_center + (-1 * self.z_factor * int(self.final_z_length / 2))

        x_end = self.x_zero + (self.x_factor * self.final_x_length)
        z_end = self.z_zero + (self.z_factor * self.final_z_length)

        self.coords = (min(self.x_zero, x_end), min(self.z_zero, z_end)
                       , max(self.x_zero, x_end), max(self.z_zero, z_end))
        self.area_expanded = (self.coords[0] - self.AREA_EXPANDED_MARGIN, self.coords[1] - self.AREA_EXPANDED_MARGIN
                              , self.final_x_length + 2 * self.AREA_EXPANDED_MARGIN
                              , self.final_z_length + 2 * self.AREA_EXPANDED_MARGIN)

        if orientation in (orientations.NORTH, orientations.SOUTH):
            self.doorLocation = ((self.x_center, self.side_wall_coordinate(orientation) + self.z_factor))
        else:
            self.doorLocation = ((self.side_wall_coordinate(orientation) + self.x_factor, self.z_center))
       
    def set_altitude(self, floor: int):
        self.y_min = floor

    def side_wall_coordinate(self, side: orientations) -> int:
            return self.coords[side.value]

    def map_coords_to_site_coords(self, x: int, y:int, z:int)-> Tuple[int, int, int]:
        #coords undergo translation and rotation
        return self.x_zero + self.x_factor * x, self.y_min + y, self.z_zero + self.z_factor * z

    def get_description(self) -> str:
        return f"{self.building_name.name} built at [{self.coords[0]},{self.coords[1]}] size: [{self.final_x_length},{self.final_z_length}] at height {self.y_min}"
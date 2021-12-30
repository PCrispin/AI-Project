import json
from typing import List
from random import choice, seed
from classes.Building import building
from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_names import building_names

class buildings(object):
    """List of all Buildings"""
    buildings = List[building]

    def __init__(self):
        data = json.load(open('data/building_maps/buildings.json'))
        self.buildings = list(map(building.from_json, data["buildings"]))

    def getByName(self, building_name: building_names) -> building :
        """Return a building by name.  eg building_names.APPLE_STORE"""
        builds = list(filter(lambda b: b.id == building_name.value , self.buildings))
        if not builds :
            return None

        return builds[0]

    def getByType(self, building_type: building_types) -> List[building] :
        """Return all buildings of a certain type.  eg building_types.HOUSE"""
        return list(filter(lambda b: b.type == building_type , self.buildings))

    def getRandomByType(self, building_type: building_types) -> building :
        """Return one random building of a certain type.  eg building_types.HOUSE"""
        builds = self.getByType(building_type)

        if not builds :
            return None

        return choice(builds)

    def getBySize(self, maxWidth: int, maxDepth: int) -> List[building] :
        """Return all buildings of a certain size.  """
        return list(filter(lambda b: b.width <= maxWidth and b.depth <= maxDepth, self.buildings))

    def getRandomBySize(self, maxWidth: int, maxDepth: int) -> building :
        """Return one random building of a certain size."""
        builds = self.getBySize(maxWidth, maxDepth)

        if not builds :
            return None

        return choice(builds)

    def getByTypeAndSize(self, building_type: building_types, maxWidth: int, maxDepth: int) -> List[building] :
        """Return all buildings of a certain type.  eg building_types.HOUSE"""
        return list(filter(lambda b: b.type == building_type and b.width <= maxWidth and b.depth <= maxDepth, self.buildings))

    def getRandomByTypeAndSize(self, building_type: building_types, maxWidth: int, maxDepth: int) -> building :
        """Return one random building of a certain type and size.  eg building_types.HOUSE less than 20x20"""
        builds = self.getByTypeAndSize(building_type, maxWidth, maxDepth)

        if not builds :
            return None

        return choice(builds)

    def getBiggestByTypeAndSize(self, building_type: building_types, maxWidth: int, maxDepth: int) -> building :
        """Return the largest building of a certain type within a specified size.  eg building_types.HOUSE less than 20x20"""
        builds = self.getByTypeAndSize( building_type, maxWidth, maxDepth)

        if not builds :
            return None

        builds.sort(key=lambda x:x.area())

        return builds[-1]

    def getBiggestBySize(self, maxWidth: int, maxDepth: int) -> building :
        """Return the largest building of a certain type within a specified size.  eg building_types.HOUSE less than 20x20"""
        builds = self.getBySize( maxWidth, maxDepth)

        if not builds :
            return None

        builds.sort(key=lambda x:x.area())

        return builds[-1]
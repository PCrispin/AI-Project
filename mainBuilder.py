from classes.ENUMS.orientations import orientations
from classes.ENUMS.building_types import building_types
from classes.ENUMS.building_names import building_names
from classes.Builder import Builder
from classes.Buildings import buildings

buildingMaps = buildings()
builder = Builder()

#structure = buildings.getRandomByType(building_types.FACTORY)
#structure = buildings.getRandomByTypeAndSize(building_types.SHOP, 25, 22)
#structure = buildings.getBiggestByTypeAndSize(building_types.FACTORY, 15, 25)
#structure = buildings.getRandomBySize(15, 25)
#structure = buildings.getBiggestBySize(15, 25)

structure = buildingMaps.getByName(building_names.APPLE_STORE)
builder.create(-163, 188, orientations.EAST, structure)

for i in range(1, 5):
    structure = buildingMaps.getRandomBySize(15, 25)
    if not builder.createAdjacentToLast(orientations.SOUTH, 1, orientations.EAST, structure):
        break

#x = 300
#for z in range(45, 130, 15) :
#    structure = buildings.getRandomBySize(15, 25)
#    builder = Builder(x, z, orientations.EAST, structure)

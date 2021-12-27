from classes.Builder import Builder
from constants import MAX_BUILDING_RADIUS, MIN_BUILDING_RADIUS
import random

#map Test 1     tp 38 100 -455
locations = [(61,-490),(37,-518),(-23,-572),(20,-560),(28,-458),(9,-477),(12,-530),(61,-563),(81,-524),(116,-491)]
building_radii = random.choices(range(MIN_BUILDING_RADIUS, MAX_BUILDING_RADIUS + 1), k = len(locations))

Builder.analyze_and_create(locations, building_radii)

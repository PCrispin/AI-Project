from classes.ENUMS.building_types import building_types
from typing import Tuple
from typing import List

class building(object):
    name = ""
    fileName = ""
    width = 0
    depth = 0
    height = 0

    type = building_types.UNKNOWN

    id = -1

    maxWidth = 0
    maxDepth = 0
    repeatableXs = []
    repeatableZs = []

    def __init__(self
                 , name: str
                 , fileName: str
                 , width: int
                 , depth: int
                 , height: int
                 , type: int
                 , id: int
                 , maxWidth: int
                 , maxDepth: int
                 , repeatableXs: str
                 , repeatableZs: str):
        self.name = name
        self.fileName = fileName
        self.width = width
        self.depth = depth
        self.height = height
        self.id = id
        self.type = building_types(type)
        self.maxWidth = maxWidth
        self.maxDepth = maxDepth
        self.repeatableXs = list(map(int, repeatableXs.split(',')))
        self.repeatableZs = list(map(int, repeatableZs.split(',')))

    def area(self):
        return self.width * self.depth

    def filePath(self) -> str :
        return 'data/building_maps/' + self.fileName

    def getRepeaters(self, requiredWidth: int, requiredDepth: int) -> Tuple[List[int], List[int]]:
        if self.maxWidth > self.width :
            requiredWidth = min(self.maxWidth, requiredWidth)
        if self.maxDepth > self.depth :
            requiredDepth = min(self.maxDepth, requiredDepth)

        moreX = max(requiredWidth - self.width, 0)
        moreZ = max(requiredDepth - self.depth, 0)

        def create(extraCount: int, available: List[int]) -> List[int]:
            reps = []

            if extraCount > 0 and available :
                for n in range[extraCount]:
                    reps.append(available[n % len(available)])
                reps.sort()

            return reps

        repX = create(moreX, self.repeatableXs)
        repZ = create(moreZ, self.repeatableZs)

        return repX, repZ

    @classmethod
    def from_json(cls, data: dict):
        return cls(**data)

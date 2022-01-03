from classes.Builder import Builder
from classes.ENUMS.orientations import orientations


Builder.build_one_of_everything(
    location=(238, 146), ground_height=3, building_face_direction=orientations.NORTH
)

from classes.Builder import Builder
from classes.ENUMS.orientations import orientations


#Builder.build_one_of_everything(
#          location = (0, 0)
#        , ground_height = 3
#        , building_face_direction = orientations.NORTH
#        )

Builder.build_one_of_everything_variable_blocks(
          location = (0, 0)
        , ground_height = 3
        , building_face_direction = orientations.NORTH
        )
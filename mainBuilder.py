from classes.Builder import Builder
from classes.ENUMS.orientations import orientations
from classes.ENUMS.block_codes import block_codes
from classes.ENUMS.building_styles import building_styles


#Builder.build_one_of_everything(
#          location = (0, 0)
#        , ground_height = 3
#        , building_face_direction = orientations.NORTH
#        )

#Builder.build_one_of_everything_variable_blocks(
#          location = (0, 0)
#        , ground_height = 3
#        , building_face_direction = orientations.NORTH
#        )

Builder.analyze_and_create(
    [(227, 188), (228, 69), (170, 61), (235, 108), (109, 207), (164, 114), (222, 40), (199, 84), (160, 13), (221, 158), (133, 169), (111, 163), (151, 181)]
    , [9, 8, 9, 11, 11, 7, 10, 8, 12, 8, 7, 11, 7]
    , block_codes.DARK_OAK_WOOD
    , building_styles.CUSTOM
    )
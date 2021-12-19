from classes.Types import GridLocation


def get_build_coord(location: GridLocation, building_radius: int) -> list:
    """Get building locations for buidling based on radius

    Args:
        location (GridLocation): Centre of the building
        building_radius ([type]): Building radius

    Returns:
        list: Vectors used to paint building
    """
    build_cord = []
    start_z = location[1] - building_radius
    end_z = (location[1] + building_radius) + 1
    for x_value in range(
        (location[0] - building_radius), ((location[0] + building_radius) + 1)
    ):
        for z_value in range(start_z, end_z):
            build_cord.append((x_value, z_value))
    return build_cord

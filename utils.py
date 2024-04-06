def get_stage_grid_positions(spacing: float = 500, grid_shape: tuple[int, int] = (3,3)
                     ) -> list[tuple[float, float]]:
    """
    Creates list of stage positions as (x, y) tuples with given spacing on a
    grid of given shape.

    Parameters:

    spacing: float
        Space between adjacent grid points in um.
    
    grid_shape: tuple[int, int]
        Desired shape of grid. Shape should be (rows, columns) as per array
        shape convention.
    
    """
    positions = []
    for x_coord in range(grid_shape[1]):
        x_pos = (x_coord - 1)*spacing
        for y_coord in range(grid_shape[0]):
            y_pos = (y_coord - 1)*spacing
            #Serpentine stage movement (obviously doesn't matter for virtual stage)
            if x_coord % 2 == 0:
                y_pos = -y_pos
            positions.append((x_pos, y_pos))
    return positions

import numpy as np
from .gridcell import GridCell

class Grid:
    """
    Represents the simulation grid as a 2D array of GridCell objects.
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Initializes a new grid of given dimensions, filling it with empty cells.

        Args:
            width (int): Number of columns in the grid.
            height (int): Number of rows in the grid.
        """
        self._width = width
        self._height = height
        self._cells = np.full((height, width), fill_value=None, dtype=object)

        for y in range(height):
            for x in range(width):
                self._cells[y, x] = GridCell()

    @property
    def width(self) -> int:
        """
        Returns the number of columns in the grid.

        Returns:
            int: Grid width.
        """
        return self._width

    @property
    def height(self) -> int:
        """
        Returns the number of rows in the grid.

        Returns:
            int: Grid height.
        """
        return self._height

    @property
    def cells(self) -> np.ndarray:
        """
        Returns the 2D array of GridCell objects.

        Returns:
            np.ndarray: The grid of cells.
        """
        return self._cells

    def get_cell(self, x: int, y: int) -> GridCell:
        """
        Returns the cell located at the given (x, y) position.

        Args:
            x (int): X-coordinate (column).
            y (int): Y-coordinate (row).

        Returns:
            GridCell: The cell at the specified position.
        """
        return self._cells[y, x]

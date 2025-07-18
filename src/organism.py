from typing import Tuple

from src.gridcell import CellState, GridCell

class Organism:
    """
    Represents a single organism within the simulation.
    Each organism has a unique ID and a position in the grid.
    """

    def __init__(self, id_: int, position: Tuple[int, int]) -> None:
        self._id = id_
        self._position = position

    @property
    def id(self) -> int:
        """
        Returns the unique identifier of the organism.

        Returns:
            int: The organism's ID.
        """
        return self._id

    @property
    def position(self) -> Tuple[int, int]:
        """
        Returns the current position of the organism in the grid.

        Returns:
            Tuple[int, int]: (x, y) position.
        """
        return self._position

    def __repr__(self) -> str:
        return f"ORG(id={self._id}, pos={self._position})"
    
    def move_to(self, cell: GridCell):
        if cell._state == CellState.RESOLVED:
            self._position = cell.position
            cell.place_org(organism=self)
        else:
            raise ValueError("Cannot move ORG to a cell not RESOLVED")
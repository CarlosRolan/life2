from typing import Optional, Tuple
from .organism import Organism

class GridCell:
    """
    Represents a single cell in the simulation grid.
    A cell may or may not be occupied by an organism.
    """

    def __init__(self, position_: Tuple[int, int]) -> None:
        self._organism: Optional[Organism] = None
        self._position: Tuple[int,int] = None
        
        
    @property
    def position(self):
        """
        Return the position of the cell as tuple(x,y)
        TODO
        Raises:
            ValueError: _description_

        Returns:
            Tuple[int,int]: The position as a tuple.
        """

    @property
    def organism(self) -> Optional[Organism]:
        """
        Returns the organism occupying this cell, if any.

        Returns:
            Optional[Organism]: The organism instance or None.
        """
        return self._organism

    @property
    def is_free(self) -> bool:
        """
        Checks whether the cell is unoccupied.

        Returns:
            bool: True if the cell is free, False otherwise.
        """
        return self._organism is None

    def places_organism(self, organism: Organism) -> None:
        """
        Places an organism into this cell.

        Args:
            organism (Organism): The organism to place.

        Raises:
            ValueError: If the cell is already occupied.
        """
        if not self.is_free:
            raise ValueError("Cell is already occupied.")
        self._organism = organism

    def empty(self) -> None:
        """
        Empties the cell, removing any organism present.
        """
        self._organism = None

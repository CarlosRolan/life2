import random
from typing import List, Optional, Tuple
import numpy as np

from src.cmd import ColorCmd, debug
from src.organism import Organism
from .gridcell import CellState, GridCell

class Grid:
    
    """
    Represents the simulation grid as a 2D array of GridCell objects.
    """
    
    # CONSTANTS
    _SCALE = 30
    _DEFAULT_WIDTH = _SCALE
    _DEFAULT_HEIGHT = _SCALE
    _DEFAULT_ORGS_DIAGONAL = [Organism(i, (i,i)) for i in range(_SCALE)]
    _DEFAULT_TRIPLE = [Organism(0, (0,0)),Organism(1, (1,0)), Organism(2, (0,1))]
    
    def __init__(self, width_: int = None, height_: int = None, organisms_: List[Organism]= None) -> None:
        """
        Initializes a new grid of given dimensions, filling it with empty cells.

        Args:
            width (int): Number of columns in the grid.
            height (int): Number of rows in the grid.
        """
            
        self._height = height_ if height_ else self._DEFAULT_HEIGHT
        self._width = width_ if width_ else self._DEFAULT_WIDTH
        self._organisms = organisms_ if organisms_ else self._DEFAULT_ORGS_DIAGONAL
        
        self._cells: dict[str:GridCell] = {}
        #Relleno el dict
        for i in range(self._height):
            for j in range(self._width):
                id_key = f"{i}_{j}"
                self._cells[id_key] = GridCell(id_key,(i,j))
        self.place_orgs_init()
        #TODO tener un array seria interesante?
        
    
        
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
    def cells(self)->dict:
        return self._cells
    
    @property
    def str_state(self):
        rows = []
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                key = self._get_key_from_pos((y,x))
                cell: GridCell = self._cells.get(key)
                if cell is None:
                    row += "."
                    continue
                row += cell.symb()
            rows.append(row)
        return '\n'.join(rows)
    
    @property
    def cmd_state(self):
        rows = []
        for y in range(self.height):
            row = ''
            for x in range(self.width):
                key = self._get_key_from_pos((y,x))
                cell: GridCell = self._cells.get(key)
                if cell is None:
                    row += "."
                    continue
                row += cell.cmd_symb
            rows.append(row)
        return '\n'.join(rows)
        
    def print_state(self) -> str:
        """
        Returns a string representation of the grid as a 2D map,
        using the current state of each GridCell (e.g., '.' for free, 'O' for occupied).
        """
        print(self.cmd_state)

    def get_organism_by_id(self, org_id: int) -> Optional[Organism]:
        """
        Retrieves an organism by its unique ID.

        Args:
            org_id (int): Organism ID.

        Returns:
            Optional[Organism]: The organism or None.
        """
        for org in self._organisms:
            if org.id == org_id:
                return org
        return None

    def get_cell(self, 
                    position: Optional[Tuple[int, int]] = None, 
                    cell_id: Optional[int] = None,
                    cell: Optional[GridCell] = None) -> Optional[GridCell]:
            """Get a cell from the grid using position, ID, or a GridCell object."""

            if position is not None:
                key = self._get_key_from_pos(position)
                return self._cells.get(key)
            
            elif cell_id is not None:
                return self._cells.get(cell_id)
            
            elif cell is not None:
                key = self._get_key_from_pos(cell.position)
                return self._cells.get(key)
            
            return None
        
    def _get_adjacent_positions(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Returns a list of all 8 adjacent positions (including diagonals)
        that are within bounds of the grid.
        """
        x, y = position
        directions = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1)
        ]

        adjacent_positions = [
            (x + dx, y + dy)
            for dx, dy in directions
            if 0 <= x + dx < self._width and 0 <= y + dy < self._height
        ]
        return adjacent_positions
    
    def _get_surrounding_cells(self, origin:Tuple[int, int] = None)->List[GridCell]:
        adjacent_positions: List[Tuple[int, int]] = self._get_adjacent_positions(origin)
        list_surr_cells: List[GridCell] = []

        for pos in adjacent_positions:
            cell = self.get_cell(pos)
            list_surr_cells.append(cell)
            
        return list_surr_cells
    
    def get_avaliable_cells(self, origin):
        list_surr_cells: List[GridCell] = self._get_surrounding_cells(origin)
        list_avaliable_cells = []

        debug("DEBUG changing all AVALIBLE cells to INTENDED")
        for cell in list_surr_cells:
            if cell.can_be_intended:
                cell.set_cell_state(CellState.INTENDED, origin)
                list_avaliable_cells.append(cell)
        return list_avaliable_cells
    
    def _get_key_from_pos(self, position: Tuple[int,int] = (0,0))-> str:
        return f"{position[0]}_{position[1]}"
            
    def place_orgs_init(self): 
        for org in self._organisms:
            cell = self.get_cell(org.position)
            if cell.is_free:
                cell.place_org(organism=org)
        print("FASE 0-Se colocan los organismos")
        print(self._organisms)
        self.print_state()
        print("FASE-0-END")
        
            
    def clean_for_next_turn(self):
        for c in self._cells.values():
            if isinstance(c, GridCell):
                if c.is_free:
                    c.clean()
        self.print_state()
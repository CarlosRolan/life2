from enum import Enum
from typing import Optional, Tuple, TYPE_CHECKING

from src.cmd.cmd import ColorCmd, my_debug
if TYPE_CHECKING:
    from ..organism.organism import Organism

class CellState(Enum):
    NOT_FREE = -1
    FREE = 0
    INTENDED = 1
    CHOSEN = 2
    CONFLICT = 3
    RESOLVED = 4 # Se ha resuelto el conflicto, se ha elegido un ganador que se movera al final de turno
    MOVING_OUT = 5
    WINNER = 6
    LOSER = 7
    BLOCKED = 8
    FULL = 9
    


class GridCell:
    """
    Represents a single cell in the simulation grid.
    A cell may or may not be occupied by an organism.
    """
   
    def __init__(self, id_, position_: Tuple[int, int]) -> None:
        self._id = id_
        self._organism: Organism = None
        self._position: Tuple[int,int] = position_
        self._state: CellState = CellState.FREE
        self._symbol: str = "•"
        # REDUNDANT
        
        
    @property
    def id(self):
        return self._id
    
    @property
    def is_chosen(self):
        return self._state == CellState.CHOSEN
    
    @property
    def is_intended(self):
        return self._state == CellState.INTENDED
    
    @property
    def cmd_color(self):
        if (self._state == CellState.FREE):
            return ColorCmd.WHITE
        elif (self._state == CellState.INTENDED):
            return ColorCmd.WHITE
        elif (self._state == CellState.CHOSEN):
            return ColorCmd.CYAN
        elif (self._state == CellState.CONFLICT):
            return ColorCmd.RED
        elif (self._state == CellState.RESOLVED):
            return ColorCmd.GREEN
        elif (self._state == CellState.MOVING_OUT):
            return ColorCmd.YELLOW
        elif self._state == CellState.LOSER:
            return ColorCmd.BLUE
        elif self._state == CellState.WINNER:
            return ColorCmd.GREEN
        elif self._state == CellState.BLOCKED:
            return ColorCmd.PURPLE
        else:
            return ColorCmd.WHITE
    
    @property
    def state(self):
        return self._state
    
    @property
    def symb(self):
        return f" {self._symbol}"
    
    @property
    def cmd_symb(self):
        return f" {self.cmd_color}{self._symbol}{ColorCmd.RESET}"

    @property
    def position(self):
        return self._position
    
    @property
    def organism(self):
        return self._organism
    
    @property
    def can_be_intended(self) -> bool:
        return self._state in (CellState.INTENDED, CellState.FREE, CellState.CHOSEN, CellState.CONFLICT)
            
    @property
    def is_free(self) -> bool:
        return self._organism is None
    
    def set_cmd_symbol(self, cmd_symbol: str) -> None:
        my_debug(f"Setting cmd_symbol={cmd_symbol} for cell {self._position}", True)
        self._symbol = cmd_symbol
    
    def set_state(self, new_state: CellState, org_pos: Optional[Tuple[int, int]] = None) -> None:
        my_debug(f"State {self.id} CHANGED [{self._state}-->{new_state}]", True)
        self._state = new_state
    
    def place_org(self, organism) -> None:
        my_debug(f"Placing {organism} in {self}")
        if not self.is_free:
            raise ValueError("Cell is already occupied.Org=",self._organism)
        self._organism = organism
        self._organism._position = self.position
        self._state = CellState.NOT_FREE
        self._symbol = f"{self._organism.id}"
    

    def empty(self):
        if self.is_free:
            raise ValueError("Cannot empty a free cell")
        my_debug(f"EMPTYING {self._position} ( o )->( )")
        self._organism = None
        self._state = CellState.FREE
        self._symbol = "."
    
    def clean(self):
        self._organism = None
        self._state = CellState.FREE
        self._symbol = "."

    def __repr__(self):
        return f"CELL{self.position}{self.state}"

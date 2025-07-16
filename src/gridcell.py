from enum import Enum
from typing import Optional, Tuple, TYPE_CHECKING

from src.cmd import ColorCmd, debug
if TYPE_CHECKING:
    from .organism import Organism

class CellState(Enum):
    NOT_FREE = -1
    FREE = 0
    INTENDED = 1
    CHOSEN = 2
    CONFLICT = 3
    RESOLVED = 4
    MOVING_OUT = 5
    WINNER = 6
    LOOSER = 7
    BLOCKED = 8
    

class GridCell:
    """
    Represents a single cell in the simulation grid.
    A cell may or may not be occupied by an organism.
    """
    
    def __init__(self, id_, position_: Tuple[int, int]) -> None:
        self._organism: Organism = None
        self._position: Tuple[int,int] = position_
        self._state: CellState = CellState.FREE
        self._symbol: str = "."
        # REDUNDANT
        self._id:str = id_
        
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
        color_map = {
            "YELLOW": "\033[33m",
            "WHITE": "\033[37m",
            "GREEN": "\033[32m",
            "RED":  "\033[31m",
            "CYAN":  "\033[36m",
            "GREY": "\033[37m",
            "BLUE": "\033[34m",
            "PURPLE": "\033[35m"
        }
        
        
        
        if (self._state == CellState.FREE):
            return color_map["WHITE"]
        elif (self._state == CellState.INTENDED):
            return color_map["WHITE"]
        elif (self._state == CellState.CHOSEN):
            return color_map["CYAN"]
        elif (self._state == CellState.CONFLICT):
            return color_map["RED"]
        elif (self._state == CellState.RESOLVED):
            return color_map["GREEN"]
        elif (self._state == CellState.MOVING_OUT):
            return color_map["YELLOW"]
        elif self._state == CellState.LOOSER:
            return color_map["BLUE"]
        elif self._state == CellState.WINNER:
            return color_map["GREEN"]
        elif self._state == CellState.BLOCKED:
            return color_map["PURPLE"]
        else:
            return color_map["WHITE"]
    
    property
    def symb(self):
        return f" {self._symbol}"
    
    @property
    def cmd_symb(self):
        RESET = "\033[0m"
        return f" {self.cmd_color}{self._symbol}{RESET}"

    @property
    def position(self):
        """
        Return the position of the cell as tuple(x,y)
        Raises:
            ValueError: _description_

        Returns:
            Tuple[int,int]: The position as a tuple.
        """
        return self._position
    
    @property
    def organism(self):
        """
        Returns the organism occupying this cell, if any.

        Returns:
            Optional[Organism]: The organism instance or None.
        """
        return self._organism
    
    @property
    def can_be_intended(self):
        return self._state == CellState.INTENDED or self._state == CellState.FREE or self._state == CellState.CHOSEN or self._state == CellState.CONFLICT
            
        

    @property
    def is_free(self) -> bool:
        """
        Checks whether the cell is unoccupied.

        Returns:
            bool: True if the cell is free, False otherwise.
        """
        return self._organism is None
    
    def set_cmd_symbol(self, org_pos=None, cmd_symbol: str = None):
        if org_pos:
            print(f"DEBUG calculating simbol for state={self._state} and old_symb={self._symbol}")
            
        # Si le paso un simbolo directo no calcula nada lo setea y punto
        if not cmd_symbol is None:
            self._symbol = cmd_symbol
            return
    
        if (self.is_chosen):
            return
        
        if(self._state == CellState.MOVING_OUT):
            self._symbol = self._organism.id
            return
        
        ox, oy = org_pos         # origen: jugador (fila, columna)
        px, py = self._position  # destino: celda actual (fila, columna)

        # Vector de movimiento desde origen hacia posición actual
        dx = px - ox  # en filas
        dy = py - oy  # en columnas

        # Normalizar a (-1, 0, 1)
        dx = (dx > 0) - (dx < 0)
        dy = (dy > 0) - (dy < 0)

        # Mapa de dirección (fila, col) ⇒ flecha
        DIRECTIONS = {
            (-1, -1): "↖",
            (-1,  0): "↑",
            (-1,  1): "↗",
            ( 0, -1): "←",
            ( 0,  0): "•",  # opcional: sin movimiento
            ( 0,  1): "→",
            ( 1, -1): "↙",
            ( 1,  0): "↓",
            ( 1,  1): "↘",
        }
        
        new_symbol = DIRECTIONS.get((dx, dy), "?")
        
        if not self._symbol == ".":
                print(f"~~SIMBOL COMBINATION~~[{self._symbol}+{new_symbol}]")
                #TODO hacer las combinaciones aqui
        
        self._symbol = new_symbol

    def place_org(self, organism) -> None:
        """
        Places an organism into this cell.

        Args:
            organism (Organism): The organism to place.

        Raises:
            ValueError: If the cell is already occupied.
        """
        debug(f"PLACING ORG={organism} -> CELL={self}")
        if not self.is_free:
            raise ValueError("Cell is already occupied.Org=",self._organism)
        self._organism = organism
        self._organism._position = self.position
        self._state = CellState.NOT_FREE
        self.set_cmd_symbol(cmd_symbol=f"o")
    
    def set_cell_state(self, new_state: CellState, origin = None):
        #TODO sacar colores a utils
        
        if (new_state == CellState.WINNER):
            debug(f"{ColorCmd.GREEN}WINNER in {self.position}")
        
        if (new_state == CellState.RESOLVED or new_state == CellState.CHOSEN) and origin is None:
            debug(f"{ColorCmd.RED}Need a position to calculate the symbol for CHOSEN | RESOLVED {self}{ColorCmd.RESET}")
        
        if (new_state == CellState.FREE):
            if not self.is_free:
                raise ValueError("CELL has organism on it, imposible to set FREE")
        
        if (new_state == CellState.INTENDED):
            if self._state == CellState.CONFLICT:
                debug(f"{ColorCmd.RED}Cell{self} CONFLICT has been {ColorCmd.BLUE}INTEDED{ColorCmd.RESET} by another ORG, stais in CONFLICT")
                return
            if self._state == CellState.CHOSEN:
                debug(f"{ColorCmd.GREEN}Cell{self} {ColorCmd.BLUE}INTENDED{ColorCmd.RESET} has been CHOSEN by another ORG, stais CHOSEN")
                return
            if self._state == CellState.RESOLVED or not self.is_free:
                raise ValueError("Cannot be INTENDED state=", self._state)
            else:
                self.set_cmd_symbol(origin)
                
        if (new_state == CellState.CHOSEN):
            if self._state == CellState.CHOSEN or self._state == CellState.CONFLICT:
                debug(f"{ColorCmd.RED}Cell {self.position} has been chosen for 1 or more organism  (changing symbol =X), now it is in CONFLICT")
                self.set_cmd_symbol(cmd_symbol="X")
                self._state = CellState.CONFLICT
                return
            elif not self.is_free:
                raise ValueError("Can only be CHOSEN cells that are INTENDED or FREE")
            
        if (new_state == CellState.CONFLICT):
            raise ValueError("Cannot set a cell in CONFLICT manually")
            
        if (new_state == CellState.RESOLVED):
            if not self._state == CellState.CONFLICT and not self._state == CellState.CHOSEN:
                raise ValueError(f"Can only be RESOLVED if the cell is in CONFLICT or has been CHOSEN ->{self}")
            else:
                self.set_cmd_symbol(origin)
        
        
        debug(f"State {self.id} CHANGED [{self._state}-->{new_state}]", True)
        self._state = new_state
    
    
    def empty(self):
        if self.is_free:
            raise ValueError("Cannot empty a free cell")
        debug(f"EMPTYING {self._position} ( o )->( )")
        self._organism = None
        self._state = CellState.FREE
        self._symbol = "."
    
    def clean(self):
        #debug(f"CLEANING {self._position}")
        self._organism = None
        self._state = CellState.FREE
        self._symbol = "."

    def __repr__(self):
        return f"{self.position}_{self._state}"

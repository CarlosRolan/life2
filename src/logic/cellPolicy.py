# policy.py
from enum import Enum
from typing import Dict, Callable, Any, Optional, Tuple

from src.cmd.cmd import DEFAULT_CELL_SYMBOL, my_debug
from .gridcell import CellState, GridCell

"""    
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
    FULL = 9"""""

class TransitionKey(Enum):
    """
    Allowed (old, candidate) pairs.
    Any (old, candidate) not present here is NOT allowed.
    """
    
    # --- NOT_FREE (origen / marcas visuales) ---
    NOT_FREE_TO_NOT_FREE   = (CellState.NOT_FREE,  CellState.NOT_FREE)
    NOT_FREE_TO_WINNER    = (CellState.NOT_FREE,  CellState.WINNER)
    NOT_FREE_TO_LOSER     = (CellState.NOT_FREE,  CellState.LOSER)
    NOT_FREE_TO_BLOCKED    = (CellState.NOT_FREE,  CellState.BLOCKED)
    NOT_FREE_TO_MOVING_OUT =  (CellState.NOT_FREE,  CellState.MOVING_OUT)
    NOT_FREE_FULL = (CellState.NOT_FREE,  CellState.FULL)

    # --- FREE ---
    FREE_TO_INTENDED     = (CellState.FREE,      CellState.INTENDED)
    
    # --- INTENDED ---
    INTENDED_TO_FREE    = (CellState.INTENDED,  CellState.FREE)
    INTENDED_TO_INTENDED = (CellState.INTENDED,  CellState.INTENDED)
    INTENDED_TO_CHOSEN   = (CellState.INTENDED,  CellState.CHOSEN)

    # --- CHOSEN ---
    CHOSEN_TO_INTENDED   = (CellState.CHOSEN,    CellState.INTENDED)    
    CHOSEN_TO_CHOSEN     = (CellState.CHOSEN,    CellState.CHOSEN)      
    CHOSEN_TO_RESOLVED   = (CellState.CHOSEN,    CellState.RESOLVED)

    # --- CONFLICT ---
    CONFLICT_TO_INTENDED = (CellState.CONFLICT,  CellState.INTENDED)   
    CONFLICT_TO_CHOSEN   = (CellState.CONFLICT,  CellState.CHOSEN)     
    CONFLICT_TO_RESOLVED = (CellState.CONFLICT,  CellState.RESOLVED)

    # --- RESOLVED(MOVING IN) ---
    RESOLVED_TO_NOT_FREE     = (CellState.RESOLVED,  CellState.NOT_FREE)
    
    # --- FULL ---
    FULL_TO_NOT_FREE     = (CellState.FULL,      CellState.NOT_FREE)
    FULL_TO_FREE     = (CellState.FULL,      CellState.FREE)

    # --- ORGS STATES ---TODO PASAR A ESTADOS DE ORG EN EL FUTURO
    # --- WINNER ---
    WINNER_TO_MOVING_OUT = (CellState.WINNER,    CellState.MOVING_OUT)
    WINNER_TO_NOT_FREE = (CellState.WINNER, CellState.NOT_FREE)
    
    # --- LOSER ---
    LOSER_TO_LOSER       = (CellState.LOSER,     CellState.LOSER)
    LOSER_TO_BLOCKED     = (CellState.LOSER,     CellState.BLOCKED)  
    LOSER_TO_WINNER     = (CellState.LOSER,     CellState.WINNER)
    LOSER_TO_MOVING_OUT = (CellState.LOSER, CellState.MOVING_OUT)
    
    # --- BLOCKED ---
    BLOCKED_TO_BLOCKED       = (CellState.BLOCKED,    CellState.BLOCKED)
    BLOCKED_TO_FREE = (CellState.BLOCKED,    CellState.FREE)
    BLOCKED_TO_NOT_FREE   = (CellState.BLOCKED,    CellState.NOT_FREE)
    
    # --- MOVING_OUT ---
    #MOVING_OUT_TO_INTENDED = (CellState.MOVING_OUT, CellState.INTENDED)
        
    @property
    def old(self) -> str:
        """
        Returns the old state in the transition.
        """
        return self.value[0]
    @property
    def candidate(self) -> str:
        """
        Returns the candidate state in the transition.
        """
        return self.value[1]

# LA NORMA GENERAL ES QUE SE ACTUALIZA AL NUEVO ESTADO CANDIDATO
STATE_LOGIC = {t:t.candidate for t in TransitionKey}

#ESTAS SON LAS EXCEPCIONES A LA NORMA GENERAL
STATE_LOGIC.update(
    {  
        # CHOSEN
        TransitionKey.CHOSEN_TO_INTENDED:   CellState.CHOSEN,    # no degradar
        TransitionKey.CHOSEN_TO_CHOSEN:     CellState.CONFLICT,  # 2º claim ⇒ CONFLICT
        TransitionKey.CHOSEN_TO_RESOLVED:   CellState.RESOLVED,  #TODO SE GANA LA CELDA SINCONFLICTO
        
        # CONFLICT
        TransitionKey.CONFLICT_TO_INTENDED: CellState.CONFLICT,  
        TransitionKey.CONFLICT_TO_CHOSEN:   CellState.CONFLICT,
    }
)

TransitionHandler = Callable[[GridCell, CellState, CellState, CellState, Optional[Tuple[int, int]]], None]

def _noop(cell: GridCell, old: CellState, candidate: CellState, computed: CellState, pos:Optional[Tuple[int, int]]) -> None:
    return

# --- Utils opcionales para símbolos ---
def _set_arrow_from_origin(cell: GridCell, origin: Tuple[int,int]) -> None:
    if origin is None:
        raise ValueError("Origin must be provided to set arrow symbol.")
    try:
        # Import local para evitar ciclos si lo mueves
        from src.cmd.cmd import calculate_cmd_arrow
        arrow = calculate_cmd_arrow(origin, cell.position)
        cell.set_cmd_symbol(arrow)
    except Exception:
        # si no existe el módulo en este entorno, ignorar
        pass

# --- Handlers de transiciones permitidas ---
# Estos son los handlers que se ejecutan cuando se aplica una transición permitida. Por defecto no ocuure nada
TRANSITION_HANDLERS: Dict[TransitionKey, TransitionHandler] = {t:_noop for t in TransitionKey}
#(cell: GridCell, old: CellState, candidate: CellState, computed: CellState, pos: Tuple[int, int])
def on_INTENDED_TO_FREE(cell: GridCell, old_state: CellState, candidate_state: CellState, computed_state: CellState) -> None:
    cell.clean()  # Limpia la celda al pasar de INTENDED a FREE
    cell.set_cmd_symbol(DEFAULT_CELL_SYMBOL)  # Limpia el símbolo de la celda

def on_INTENDED_TO_INTENDED(cell: GridCell, old: CellState, candidate: CellState, computed: CellState, pos: Tuple[int, int]):
    _set_arrow_from_origin(cell, pos)
    
def on_MOVING_OUT_TO_FREE(cell: GridCell, old: CellState, candidate: CellState, computed: CellState, pos: Tuple[int, int]):
    cell.empty()
    
def on_CONFLICT_TO_RESOLVED(cell: GridCell, old: CellState, candidate: CellState, computed: CellState, pos: Tuple[int, int]):
    _set_arrow_from_origin(cell, pos)
    
def on_CHOSEN_TO_CHOSEN(cell: GridCell, old: CellState, candidate: CellState, computed: CellState, pos: Tuple[int, int]):
    cell.set_cmd_symbol("X")
    
def on_FREE_TO_INTENDED(cell: GridCell, old: CellState, candidate: CellState, computed: CellState, pos: Tuple[int, int]):
    _set_arrow_from_origin(cell, pos)
    
def ON_WINNER_TO_NOT_FREE(cell: GridCell, old: CellState, candidate: CellState, computed: CellState, pos: Tuple[int, int]):
    print("Se cambia de winner a free ahora",cell)
    
TRANSITION_HANDLERS.update({
    # --- FREE ---
    TransitionKey.FREE_TO_INTENDED: on_FREE_TO_INTENDED,
    # --- INTENDED ---
    TransitionKey.INTENDED_TO_INTENDED: on_INTENDED_TO_INTENDED,  #TODO ARROW COMBINATION
    TransitionKey.INTENDED_TO_FREE: on_INTENDED_TO_FREE,  # limpia la flecha

    # --- CHOSEN ---
    TransitionKey.CHOSEN_TO_CHOSEN: on_CHOSEN_TO_CHOSEN, 
    
    # --- CONFLICT ---
    TransitionKey.CONFLICT_TO_RESOLVED: on_CONFLICT_TO_RESOLVED,  # coloca flecha de movimiento
})

#FUNCOIN QQUE CALCULA EL ESTADO GRACIAS A LA LOGICA HECHA CON DICCIONARIOS 
def compute_state(old_state: CellState, candidate_state: CellState) -> CellState:
    
    my_debug(f"Computing state from {old_state.name} to {candidate_state.name}")

    try:
        transition_key = TransitionKey((old_state, candidate_state))
    except ValueError:
        #TODO ERRORES CON EL ESTADO DE LA CELL
        if candidate_state is CellState.CONFLICT:
            raise ValueError("Cannot set CONFLICT directly; set CHOSEN to derive it.")
        if candidate_state is CellState.WINNER and old_state is not CellState.CONFLICT:
            raise ValueError("Cannot mark WINNER on a cell wit NO CONFLICT.")
        if candidate_state is CellState.RESOLVED and old_state not in (CellState.CHOSEN, CellState.CONFLICT):
            raise ValueError(f"Can only set RESOLVED from CHOSEN/CONFLICT nor can be setted up RESOLVED AGAIN[{old_state.name} -> {candidate_state.name}]")
        raise ValueError(f"Transition {old_state.name} -> {candidate_state.name} is not allowed.")

    computed_state = STATE_LOGIC.get(transition_key)
    
    # IMPORTANT no deberia ser necesario pero nos indica si no tenenmos sincronizado las transiciones del enum con las transiciones permitidas
    if computed_state is None:
        raise ValueError(f"Transition {old_state.name} -> {candidate_state.name} is not defined.")
    
    return computed_state


def apply_state_transition(cell: GridCell, candidate_state: CellState,
                     org_pos: Optional[Tuple[int, int]] = None) -> CellState:

    #Compute + apply + handler:
     # 1) Calcula el estado aplicado desde (cell.state, candidate)
      #2) Aplica el estado a la celda
      #3) Llama al handler específico de la transición permitida
    #Devuelve el estado aplicado.
  
    old_state = cell.state
    
    #TODO ERRORES CON LAS OTROS PRIPIEDADES DE LA CELL
    if candidate_state is CellState.WINNER:
        if cell.is_free:
            raise ValueError("Cannot set WINNER on a cell that is free.") 

    # 1) compute
    computed_state = compute_state(old_state, candidate_state)

    # 2) apply
    cell.set_state(computed_state)

    # 3) handler
    t = TransitionKey((old_state, candidate_state))
    handler = TRANSITION_HANDLERS.get(t)
    if handler:
        handler(cell, old_state, candidate_state, computed_state, org_pos)

    return computed_state
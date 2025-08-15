import random
from typing import List, Tuple, Dict, Optional

from src.cmd.cmd import ColorCmd, calculate_cmd_arrow, my_debug

from .grid import Grid
from ..organism.organism import Organism
from .gridcell import GridCell, CellState
from .cellPolicy import TransitionKey, TransitionHandler,apply_state_transition

class Simulation:
    """
    Manages the evolutionary simulation, including grid state, organisms,
    and the turn-based update logic.
    """

    def __init__(self, grid_: Grid = None) :
        
        self._turn = 0
        self._n_total_intentions = 0
        self._n_total_conflicts = 0
        
        self._chosen_moves: Dict[int: Tuple[int, int]] = {}
        
        self._conflicts: Dict[Tuple[int, int]: List[int]] = {}
        
        self._comfirmed_moves: Dict[Tuple[int, int]: int] = {}
        
        self._grid = grid_ if grid_ else Grid()
            
        
    def calculate_intentions(self, orgs: List[Organism]):
        # FASE 1----------------------
        print("CALCULATION PHASE-[START]------------------------)")
        my_debug(f"ORGANISMS to calculate {orgs}")
        cells_to_intent = []
        if not orgs is None:
            for o in orgs:
                org_pos = o.position
                cells_to_intent = self._get_avaliable_cells(org_pos)
                
                for cell in cells_to_intent:
                    apply_state_transition(cell, CellState.INTENDED, org_pos=org_pos) # FREE->INTEDED
                
                # Si no tiene celdas a las que se puede mover bloqueamos a la celda del orgnaismo y queda BLOCKED
                if len(cells_to_intent) == 0: 
                    my_debug(f"{ColorCmd.PURPLE}[{o.id}]{o.position} => BLOCKED")
                    
                    cell_of_org = self._grid.get_cell(org_pos) # es NOT_FREE ahora
                    apply_state_transition(cell_of_org, CellState.BLOCKED) # NOT_FREE -> BLOCKED
                    
                    continue
                
                else:
                    my_debug(f"ORG=[{o.id}]{o.position} CELLs=>{cells_to_intent}", False)
                    
                    #==============================Escojemos una celda al azar de las INTENDED
                    chosen_cell = random.choice(cells_to_intent) #aqui es INTEDED o CHOSEN de otro
                    
                    my_debug(f"{ColorCmd.CYAN}CHOSEN_MOVE [{o}]=>[{chosen_cell}]")
                    
                    # INTENDED -> CHOSEN
                    # CHOSEN -> CHOSEN (esto lo setea a conflict)
                    apply_state_transition(chosen_cell, CellState.CHOSEN) 
                    
                    self._chosen_moves[o.id] = chosen_cell.position 
                                       
        orgs_for_cell = {}
        
        # Gracias a mi logica de estado las celdas en conflicto ya tienen su estado a CONFLICT
        # ORGS_FOR_CELL para caluclar conflictos
        for org_id, pos in self._chosen_moves.items():
            if pos in orgs_for_cell:
                orgs_for_cell[pos].append(org_id)
            else:
                orgs_for_cell[pos] = [org_id]
        
        # Es un conflicto si hay mas de 1 id de organismo(orgs_ids) por posicion de celda(pos)
        self._conflicts = {pos: org_ids for pos, org_ids in orgs_for_cell.items() if len(org_ids) > 1}
            
        #Si solo hay uno es que nadie más ha escogido la celda y lo marcamos como listo para moverse
        # Celda de destino será -> RESOLVED
        # Celda de origen será -> MOVING_OUT
        self._comfirmed_moves = {pos: org_ids[0] for pos, org_ids in orgs_for_cell.items() if len(org_ids) == 1}      
        
        print(f"·INTENTIONS =   (white arrows) {cells_to_intent}")
        print(f"{ColorCmd.CYAN}·CHOSEN_MOVES = (cyan arrows) {self._chosen_moves}{ColorCmd.RESET}")
        print(f"{ColorCmd.RED}·CONFLICTS =    (red crosses) {self._conflicts}{ColorCmd.RESET}")
        
        self._grid.print_state()
        print("CALCULATION-PHASE-[END]------------------------)\n")
            
    def _mark_conflicts(self):
        pass
    def _validate_comfirmed_cells(self):
        
        print("VALIDATION PHASE-[START]------------------------)")
        print("Validating chosen cells...")
        my_debug(f"{ColorCmd.GREEN}CHOSEN = (cyan arrows) {ColorCmd.WHITE} {self._comfirmed_moves}")
        my_debug(f"Passing {ColorCmd.CYAN}CHOSEN{ColorCmd.RESET} ->{ColorCmd.GREEN}RESOLVED{ColorCmd.WHITE}")
        
        #VALIDAMOS LOS comfirmed moved que era los chosen moves con un solo org id
        for pos, org_id in self._comfirmed_moves.items():
            
            org_ready = self._get_org_in_grid(org_id)
            cell_of_org = self._grid.get_cell(org_ready.position) 
            
            apply_state_transition(cell_of_org, CellState.MOVING_OUT) # NOT_FREE-> MOVING_OUT
            
            cell_to_move = self._grid.get_cell(pos) 
            
            apply_state_transition(cell_to_move, CellState.RESOLVED, org_pos=org_ready.position) #CHOSEN-> RESOLVED
        
        self._grid.print_state()
        print("VALIDATION PHASE-[END]------------------------)\n")
    
    def _resolve_conflicts(self):
        
        i = 0
        
        list_orgs_loosers = []
        
        while self._conflicts:   
            print(f"{ColorCmd.RED}CONFLICTS-PHASE IN TURN:{self._turn}-[START]------------------------){ColorCmd.RESET}")        
            for conflict_pos, list_orgs_id_in_conflict in self._conflicts.copy().items():
                i += 1
                print(f"{ColorCmd.RED}CONFLICT_{i}_={conflict_pos}{ColorCmd.RESET} ORGS={list_orgs_id_in_conflict}")
                
                #IMPORTANTE SE ESCOGEEEEEE 1 ganador===============================================
                winner_org_id = random.choice(list_orgs_id_in_conflict)  
                
                # Sacamos el ganador de la lista de ids en conflicto
                list_orgs_id_in_conflict.remove(winner_org_id)
                
                #Añadimos a COMFIRMED EL GANADOR DEL CONFLICTO
                self._comfirmed_moves[conflict_pos] = [winner_org_id]
                
                # CELL GANADORA
                org_winner = self._get_org_in_grid(winner_org_id)
                cell_winner = self._grid.get_cell(org_winner.position)
                apply_state_transition(cell_winner, CellState.WINNER) # LOSER->WINNER o  NOT_FREE->WINNER
                
                # CELULA(S) PERDEDORAS            
                for losser_id in list_orgs_id_in_conflict:
                    org_looser = self._get_org_in_grid(losser_id)
                    list_orgs_loosers.append(org_looser)
                    
                    cell_looser = self._grid.get_cell(org_looser.position)
                    # LOSER->WINNER o  NOT_FREE->WINNER
                    apply_state_transition(cell_looser, CellState.LOSER, org_pos=org_winner.position)
                
                # CELL EN CONFLICTO
                cell_conflict = self._grid.get_cell(conflict_pos)
                # CONFLICT -> RESOLVED
                apply_state_transition(cell_conflict, CellState.RESOLVED, org_pos=org_winner.position)
                
                # Por ultimo eliminamos del diccionario de conflictos el conflicto resuelto en la iteracion
                del self._conflicts[conflict_pos]
                
                print(f"\t{ColorCmd.GREEN}·WINNER=[{winner_org_id}]{ColorCmd.RESET}")
                print(f"{ColorCmd.BLUE}·LOOSERS={list_orgs_id_in_conflict}{ColorCmd.RESET}")
                print(f"{ColorCmd.RED}CONFLICTS-PHASE IN TURN:{self._turn}-[END]------------------------){ColorCmd.RESET}\n")
            
            # Vemos la cuadricula con la primera ronda de conflictos resulta pero los perdedores peuden generar mas conflictos
            self._grid.print_state()
            
            print("LIST_ORG_LOOSERS_ROUND", list_orgs_loosers)
            print("Calculating now moves for LOOSERS")
            
            # IMPORTANT: reset per-turn state before a new sub-round
            self._chosen_moves.clear()
            self._comfirmed_moves.clear()
            self.calculate_intentions(list_orgs_loosers)
            
    def _apply_moves(self):
        print("Hay que aplicar acciones ", self._comfirmed_moves)

        if self._comfirmed_moves:        
            print("FASE 3-APLICANDO CAMBIOS")
            print(self._comfirmed_moves)
            #Aplicamos los movimientos aqui
            for pos, list_org in self._comfirmed_moves.items():
                             
                org_to_move = self._get_org_in_grid(list_org)
                
                cell_of_org = self._grid.get_cell(org_to_move.position)
                cell_of_org.empty()
                
                cell_to_move = self._grid.get_cell(pos)
                cell_to_move.place_org(org_to_move)
                
            print("FASE 4-APLICANDO CAMBIOS-[END]\n")
        else:
            print("NOTHING TO CHANGE")
    
    def pass_turn(self):
        
        self._turn += 1
        
        self.calculate_intentions(self._grid._organisms)    
                
        self._resolve_conflicts()
        
        self._apply_moves()
        
        
        
    def random_cell_chose(pos_list: List[Tuple]):
        pass
    
    def _get_org_in_grid(self, org_id: int):
        return self._grid.get_organism_by_id(org_id)
    
    def pritn_grid_state(self):
        self._grid.print_state()
    
    def _get_avaliable_cells(self, origin) -> List[GridCell]:
        list_surr_cells: List[GridCell] = self._grid._get_surrounding_cells(origin)

        list_avaliable_cells = []

        for cell in list_surr_cells:
            if cell.can_be_intended: 
                list_avaliable_cells.append(cell)
            else:
                my_debug(f"Cell {cell.position} cannot be INTENDED, state={cell.state}")
        return list_avaliable_cells  
    

    
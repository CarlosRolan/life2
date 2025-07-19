import random
from typing import List, Tuple, Dict, Optional

from src.cmd import ColorCmd, debug

from .grid import Grid
from .organism import Organism
from .gridcell import GridCell, CellState

class Simulation:
    """
    Manages the evolutionary simulation, including grid state, organisms,
    and the turn-based update logic.
    """

    def __init__(self, grid_: Grid = None) :
        
        self._turn = 0
        self._n_total_intentions = 0
        self._n_total_conflicts = 0
        
        self.grid = grid_ if grid_ else Grid()
            
        
    def calculate_intentions(self, orgs: List[Organism]):
        # FASE 1----------------------
        print("CALCULATION PHASE-[START]------------------------)")
        debug(f"ORGANISMS to calculate {orgs}")
        chosen_moves: Dict[Tuple[int, int]: List[GridCell]] = {}
        if not orgs is None:
            for o in orgs:
                org_pos = o.position
                cells_for_org = self.grid.get_avaliable_cells(org_pos)
                
                if len(cells_for_org)== 0: 
                    debug(f"{ColorCmd.PURPLE}[{o.id}]{o.position} => BLOCKED")
                    cell_of_org = self.grid.get_cell(org_pos)
                    cell_of_org.set_cell_state(CellState.BLOCKED)
                    continue
                else:
                    debug(f"AVAL_CELLs=[{o.id}]{o.position} =>{cells_for_org}")
                    
                if type(cells_for_org) is list:
                    #SE ESCOGE UNA CELDA DE LAS OPCIONES POSIBLES
                    chosen_cell = random.choice(cells_for_org)
                    debug(f"{ColorCmd.CYAN}CHOSEN_MOVE FOR={o.position} =>{chosen_cell.position} [{o}]=>[{chosen_cell}]")
                    chosen_cell.set_cell_state(CellState.CHOSEN, org_pos)
                    chosen_moves[o.id] = chosen_cell.position
                    
                    
        orgs_for_cell = {}
        
        # Paso 1: construir un diccionario pos → lista de orgs
        for org_id, pos in chosen_moves.items():
            if pos in orgs_for_cell:
                orgs_for_cell[pos].append(org_id)
            else:
                orgs_for_cell[pos] = [org_id]
        
        
        conflicts = {pos: org_ids for pos, org_ids in orgs_for_cell.items() if len(org_ids) > 1}
        comfirmed_moves = {pos: org_ids for pos, org_ids in orgs_for_cell.items() if len(org_ids) == 1}
        
        print(f"·INTENTIONS = (white arrows) {cells_for_org}")
        print(f"·{ColorCmd.CYAN}CHOSEN_MOVES = (cyan arrows) {chosen_moves}{ColorCmd.RESET}")
        print(f"·{ColorCmd.RED}CONFLICTS = (red crosses) {conflicts}{ColorCmd.RESET}")
        
        self.grid.print_state()
        print("CALCULATION-PHASE-[END]------------------------)\n")
        self.validate_comfirmed_cells(comfirmed_moves)
            
        return conflicts, comfirmed_moves
    
    def validate_comfirmed_cells(self, comfirmed_moves):
        
        print("VALIDATION PHASE-[START]------------------------)")
        print("Validating chosen cells...")
        debug(f"Passing a {ColorCmd.CYAN}CHOSEN{ColorCmd.RESET} ->{ColorCmd.GREEN}RESOLVED{ColorCmd.WHITE}")
        debug(f"·{ColorCmd.GREEN}CHOSEN = (cyan arrows) {ColorCmd.WHITE} {comfirmed_moves}")
        #VALIDAMOS LOS CHOSEN DE 1 (sin conflicto) a RESOLVED
        for pos, org_id in comfirmed_moves.items():
            org_to_move = self._get_org_in_grid(org_id[0])
            cell_org = self.grid.get_cell(org_to_move.position)
            cell_org.set_cell_state(CellState.MOVING_OUT)
            
            cell_to_move = self.grid.get_cell(pos)
            if (not cell_to_move._state is CellState.RESOLVED):
                cell_to_move.set_cell_state(CellState.RESOLVED, org_to_move.position)
        
        self.grid.print_state()
        print("VALIDATION PHASE-[END]------------------------)\n")
    
    def resolve_conflicts(self, conflicts, comfirmed_moves):
        
        i = 0
            
        print(f"{ColorCmd.RED}CONFLICTS-PHASE IN TURN:{self._turn}-[START]------------------------)")
        list_orgs_loosers = []
        for conflict_pos, list_orgs_id in conflicts.items():
            i += 1
            print(f"{ColorCmd.RED}CONFLICT_{i}_={conflict_pos}{ColorCmd.RESET} ORGS={list_orgs_id}")
            winner_id = random.choice(list_orgs_id)
            print(f"{ColorCmd.GREEN}·WINNER=[{winner_id}]{ColorCmd.RESET}")
            # Sacamos el ganador de la lista de ids en conflicto para pos
            list_orgs_id.remove(winner_id)
            
            #Añadimos a COMFIRMED EL GANADOR DEL CONFLICTO
            comfirmed_moves[conflict_pos] = [winner_id]
            
            # CELULA GANADORA
            org_winner = self._get_org_in_grid(winner_id)
            
            cell_winner = self.grid.get_cell(org_winner.position)
            cell_winner.set_cell_state(CellState.WINNER)
            
            #CELULA EN CONFLICTO
            cell_conflict = self.grid.get_cell(conflict_pos)
            cell_conflict.set_cell_state(CellState.RESOLVED, cell_winner.position)
            
            # CELULA(S) PERDEDORAS
            print(f"{ColorCmd.BLUE}·LOOSERS={list_orgs_id}{ColorCmd.RESET}")
            
            for losser_id in list_orgs_id:
                org_looser = self._get_org_in_grid(losser_id)
                list_orgs_loosers.append(org_looser)
                
                cell_looser = self.grid.get_cell(org_looser.position)
                cell_looser.set_cell_state(CellState.LOOSER)
                
        print(f"{ColorCmd.RED}CONFLICTS-PHASE IN TURN:{self._turn}-[END]------------------------){ColorCmd.RESET}\n")
        
        self.grid.print_state()
        
        return list_orgs_loosers
    
    def pass_turn(self):
        
        self._turn += 1
        
        conflicts, comfirmed_moves = self.calculate_intentions(self.grid._organisms)
        
        list_orgs_loosers = []
        while True:
            
            if len(conflicts.values()) == 0:
                print(f"ALL CONFLICTS RESUELT FOR THISSS TURNNN{self._turn}")
                break
            else:
                print("ALL_COMFLICTS", conflicts)
                
            list_orgs_loosers_round = self.resolve_conflicts(conflicts, comfirmed_moves)
            list_orgs_loosers += list_orgs_loosers_round
            
            print("LIST_ORG_LOOSERS_ROUND", list_orgs_loosers_round)
            
            print("Calculating now moves for LOOSERS")
            conflicts, comfirmed_moves = self.calculate_intentions(list_orgs_loosers)
            
            
        print("Hay que aplicar acciones ", comfirmed_moves)
        
        if comfirmed_moves:
            print("FASE 3-APLICANDO CAMBIOS")
            print(comfirmed_moves)
            #Aplicamos los movimientos aqui
            for pos, list_org in comfirmed_moves.items():
                if len(list_org) != 1:
                    raise ValueError("COMFIRMED MOVES CANNOT HAVE MORE THAN 1 org")
                org_to_move = self._get_org_in_grid(list_org[0])
                
                cell_of_org = self.grid.get_cell(org_to_move.position)
                cell_of_org.empty()
                
                cell_to_move = self.grid.get_cell(pos)
                cell_to_move.place_org(org_to_move)
                
            print("FASE 4-APLICANDO CAMBIOS-[END]\n")
            self.grid.clean_for_next_turn()
        else:
            print("NOTHING TO CHANGE")
        
    def random_cell_chose(pos_list: List[Tuple]):
        pass
    def _get_org_in_grid(self, org_id: int):
        return self.grid.get_organism_by_id(org_id)
    
    def pritn_grid_state(self):
        self.grid.print_state()
        
    
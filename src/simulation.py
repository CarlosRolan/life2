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
        self.grid = grid_ if grid_ else Grid()
            
        
    def calculate_intentions(self, orgs: List[Organism]):
        # FASE 1----------------------
        print("CALCULATION PHASE-[START]------------------------)")
        print("ORGANISMS to calculate", orgs)
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
                    
                    
            debug(f"\tCHOSE_MOVES{chosen_moves}")
                    
        orgs_for_cell = {}
        
        # Paso 1: construir un diccionario pos → lista de orgs
        for org_id, pos in chosen_moves.items():
            if pos in orgs_for_cell:
                orgs_for_cell[pos].append(org_id)
            else:
                orgs_for_cell[pos] = [org_id]
                
        conflicts = {pos: org_ids for pos, org_ids in orgs_for_cell.items() if len(org_ids) > 1}
        comfirmed = {pos: org_ids for pos, org_ids in orgs_for_cell.items() if len(org_ids) == 1}
        
        
        print(f"Intentions (white arrows) {orgs_for_cell}")
        print(f"CONFLICTS {ColorCmd.RED}(red crosses) {conflicts}")
        print(f"CHOSEN {ColorCmd.BLUE}(blue arrows) {comfirmed}")
        self.grid.print_state()
        print("CALCULATION-PHASE-[END]------------------------)")
            
        return conflicts, comfirmed
    
    def validate_resolved_cells(self, comfirmed_moves):
        
        print("VALIDATION PHASE-[START]------------------------)")
        print("Validating chosen cells...")
        #VALIDAMOS LOS CHOSEN DE 1 (sin conflicto) a RESOLVED
        for pos, org_id in comfirmed_moves.items():
            org_to_move = self._get_org_in_grid(org_id[0])
            cell_org = self.grid.get_cell(org_to_move.position)
            cell_org.set_cell_state(CellState.MOVING_OUT)
            
            cell_to_move = self.grid.get_cell(pos)
            if (not cell_to_move._state is CellState.RESOLVED):
                cell_to_move.set_cell_state(CellState.RESOLVED, org_to_move.position)
        print("VALIDATION PHASE-[END]------------------------)")
        
    def pass_turn(self):
        
        self._turn += 1
        
        conflicts, comfirmed_moves = self.calculate_intentions(self.grid._organisms)
        
        self.validate_resolved_cells(comfirmed_moves)
        
        i= 0
    
        while True:
            i += 1
            if len(conflicts.values()) == 0:
                print("NO CONFLICTS-------------------")
                break
            
            debug(f"Resolving CONFLICTS iteration:{i}")
            
            for conflict_pos, list_orgs_id in conflicts.items():
                x = str(ColorCmd.RED)
                debug(f"-------------------{x}CONFLICT:{conflict_pos}{ColorCmd.RESET}")
                winner_id = random.choice(list_orgs_id)
                debug(f"{ColorCmd.GREEN}\tWINNER=[{winner_id}]{ColorCmd.RESET}")
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
                debug(f"{ColorCmd.BLUE}\tLOOSERS={list_orgs_id}{ColorCmd.RESET}")
                for losser_id in list_orgs_id:
                    org_looser = self._get_org_in_grid(losser_id)
                    
                    cell_looser = self.grid.get_cell(org_looser.position)
                    cell_looser.set_cell_state(CellState.LOOSER)
                
                i+=1
                
                self.grid.print_state()
                
            if len(conflicts.values()) == 0:
                self.grid.print_state()
                print("-------------------CONFLICTs DONE") 
                break
            else:
                list_orgs_pending = []
                
                for pos, list_loosers_id in conflicts.items():
                    for looser_id in list_loosers_id:
                        org_looser = self._get_org_in_grid(looser_id)
                        cell_org_looser = self.grid.get_cell(org_looser.position)
                        cell_org_looser.set_cell_state(CellState.NOT_FREE) 
                        list_orgs_pending.append(org_looser)
                    
                print("ORGS a recalcular", list_orgs_pending)
                
                conflicts, comfirmed_moves_for_winners = self.calculate_intentions(list_orgs_pending)
                
                comfirmed_moves = {**comfirmed_moves, **comfirmed_moves_for_winners}
                
                
                # TODO conseguir los organismos nuevos que tiene que paser de CHOSEN a RESOLVED
                #comfirmed_moves = [self._get_org_in_grid(org_id[0]) for org_id in comfirmed_moves.values()]
                self.validate_resolved_cells(comfirmed_moves)
                print("DEBUG TOTAL_COMFIRMED", comfirmed_moves)
                self.grid.print_state()
        
            
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
                
            print("FASE 4-APLICANDO CAMBIOS-[END]")
            self.grid.clean_for_next_turn()
            self.grid.print_state()
        else:
            print("NOTHING TO CHANGE")
        
    def random_cell_chose(pos_list: List[Tuple]):
        pass
    def _get_org_in_grid(self, org_id: int):
        return self.grid.get_organism_by_id(org_id)
    
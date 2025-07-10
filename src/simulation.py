import random
from typing import List, Tuple, Dict, Optional

from .grid import Grid
from .organism import Organism
from .gridcell import GridCell

class Simulation:
    """
    Manages the evolutionary simulation, including grid state, organisms,
    and the turn-based update logic.
    """

    def __init__(self, width: int, height: int, num_organisms: int) -> None:
        """
        Initializes the simulation grid and populates it with organisms
        placed randomly in free cells.

        Args:
            width (int): Grid width.
            height (int): Grid height.
            num_organisms (int): Number of organisms to initialize.
        """
        self.grid = Grid(width, height)
        self.organisms: List[Organism] = []

        placed = 0
        while placed < num_organisms:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            cell = self.grid.get_cell(x, y)

            if cell.is_free:
                org = Organism(id_=placed, position=(x, y))
                cell.places_organism(org)
                self.organisms.append(org)
                placed += 1

    def next_turn(self) -> None:
        """
        Advances the simulation by one full turn, applying
        a three-phase model to resolve all organism actions.
        """
        intentions: Dict[int, Tuple[int, int]] = self._evaluate_intentions()
        print("SETTING INTENTIOS-------------------")
        print(intentions)
        confirmed_actions: Dict[int, Tuple[int, int]] = self._resolve_conflicts(intentions)
        print("COMFIRMED ACTIONS-------------------")
        print(confirmed_actions)
        self._apply_actions(confirmed_actions)
        print("APPLYING ACTIONS to GRID")
        self.print_grid()

    def _evaluate_intentions(self) -> Dict[int, Tuple[int, int]]:
        """
        Phase 1: Each organism evaluates its surroundings and proposes a target cell.

        Returns:
            Dict[int, Tuple[int, int]]: Proposed new positions per organism ID.
        """
        intentions = {}

        for org in self.organisms:
            x, y = org.position
            neighbors = self._get_adjacent_positions(x, y)
            #print(self._get_surrounding_cells(neighbors))
            print(neighbors)
            free_neighbors = [
                pos for pos in neighbors
                if self.grid.get_cell(*pos).is_free
            ]
            if free_neighbors:
                target = random.choice(free_neighbors)
                intentions[org.id] = target

        return intentions

    def _resolve_conflicts(self, intentions: Dict[int, Tuple[int, int]]) -> Dict[int, Tuple[int, int]]:
        """
        Phase 2: Resolves conflicts where multiple organisms attempt to move to the same cell.

        Args:
            intentions (Dict[int, Tuple[int, int]]): Proposed positions.

        Returns:
            Dict[int, Tuple[int, int]]: Final allowed actions after conflict resolution.
        """
        cell_claims: Dict[Tuple[int, int], List[int]] = {}
        for org_id, pos in intentions.items():
            cell_claims.setdefault(pos, []).append(org_id)

        confirmed: Dict[int, Tuple[int, int]] = {}
        for pos, claimers in cell_claims.items():
            if len(claimers) == 1:
                confirmed[claimers[0]] = pos
            else:
                winner = random.choice(claimers)
                confirmed[winner] = pos

        return confirmed

    def _apply_actions(self, confirmed: Dict[int, Tuple[int, int]]) -> None:
        """
        Phase 3: Applies the confirmed actions to update the grid and organism positions.

        Args:
            confirmed (Dict[int, Tuple[int, int]]): Final moves.
        """
        for org_id, new_pos in confirmed.items():
            org = self._get_organism_by_id(org_id)
            if org is None:
                continue
            #Eliminas el organismo de la celda
            old_x, old_y = org.position
            self.grid.get_cell(old_x, old_y).empty()
            
            #Colocamos el organismo en la nueva celda
            new_x, new_y = new_pos
            self.grid.get_cell(new_x, new_y).places_organism(org)
            org._position = (new_x, new_y)  # internal update
    
    def _get_adjacent_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Returns a list of valid orthogonal neighbor positions.

        Args:
            x (int): X-coordinate.
            y (int): Y-coordinate.

        Returns:
            List[Tuple[int, int]]: List of (x, y) neighbor positions.
        """
        candidates = [
            (x - 1, y), (x + 1, y),
            (x, y - 1), (x, y + 1)
        ]
        return [
            (nx, ny) for nx, ny in candidates
            if 0 <= nx < self.grid.width and 0 <= ny < self.grid.height
        ]

    def _get_adjacent_positions2(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
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

        adjacent = [
            (x + dx, y + dy)
            for dx, dy in directions
            if 0 <= x + dx < self._width and 0 <= y + dy < self._height
        ]
        return adjacent
    
    def _get_surrounding_cells(self, adjacent_positions: List[Tuple[int, int]] = None, cell_pos:Tuple[int, int] = None):
        list_surr_cells: List[GridCell] = []
        if cell_pos == None:
            for pos in adjacent_positions:
                surr_cell = self.grid.get_cell(pos[0], pos[1])
                list_surr_cells.append(surr_cell)
            return list_surr_cells
        else:
            return self._get_surrounding_cells(self._get_adjacent_positions(cell_pos))
            

    def _get_organism_by_id(self, org_id: int) -> Optional[Organism]:
        """
        Retrieves an organism by its unique ID.

        Args:
            org_id (int): Organism ID.

        Returns:
            Optional[Organism]: The organism or None.
        """
        for org in self.organisms:
            if org.id == org_id:
                return org
        return None

    def print_grid(self) -> None:
        """
        Prints a visual representation of the grid to the console,
        showing organism IDs or dots for empty cells.
        """
        for y in range(self.grid.height):
            row = ""
            for x in range(self.grid.width):
                cell = self.grid.get_cell(x, y)
                row += f"{cell.organism.id if not cell.is_free else '.':>3}"
            print(row)
        print()



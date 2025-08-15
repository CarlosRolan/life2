from enum import Enum
from typing import Tuple
import os

debugging = False

#Los metodos de printear de la clase grid deberiar ir aqui, no el archivo grid.py y que este archivos sea el que tenga un metodo que llame a print con el cmd_state

DEFAULT_CELL_SYMBOL = "•"
DIRECTION_SYMBOLS = {
    (-1, -1): "↖",  (-1,  0): "↑",  (-1,  1): "↗",
    ( 0, -1): "←",  ( 0,  0): "•",  ( 0,  1): "→",
    ( 1, -1): "↙",  ( 1,  0): "↓",  ( 1,  1): "↘",
}

class ColorCmd(Enum):
  YELLOW = "\033[33m"
  WHITE = "\033[37m"
  GREEN = "\033[32m"
  RED =  "\033[31m"
  CYAN =  "\033[36m"
  GREY = "\033[37m"
  BLUE = "\033[34m"
  PURPLE= "\033[35m"
  RESET = "\033[0m"
  
  def __str__(self):
        return str(self.value)
      
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def calculate_cmd_arrow(origin: Tuple[int, int], final: Tuple[int, int]):
   
    my_debug(f"Calculating simbol in position={final}")      
    
    ox, oy = origin         # origen: jugador (fila, columna)
    px, py =  final          # destino: celda actual (fila, columna)

    # Vector de movimiento desde origen hacia posición actual
    dx = px - ox  # en filas
    dy = py - oy  # en columnas

    # Normalizar a (-1, 0, 1)
    dx = (dx > 0) - (dx < 0)
    dy = (dy > 0) - (dy < 0)

    new_symbol = DIRECTION_SYMBOLS.get((dx, dy), "?")
    
    #TODO hacer las combinaciones aqui
    
    return new_symbol
  
def my_debug(msg, verbose = None):
  if not debugging:
    return
  if verbose is None:  
      print(f"[DEBUG]__{msg}{ColorCmd.RESET}")
  else:
    #Si tiene el parametro de verbose solo se mostrara si dicho parametro es TRUE
    if verbose:
      print(f"[DEBUG_VERBOSE]__{msg}{ColorCmd.RESET}")
      
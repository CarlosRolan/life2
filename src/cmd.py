from enum import Enum

 
debugging = False

def debug(msg, verbose = None):
  if not debugging:
    return
  if verbose is None:  
      print(f"DEBUG {msg}")
  else:
    if verbose:
      print(f"DEBUG {msg}")

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
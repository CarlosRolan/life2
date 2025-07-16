import sys
import os

# Añadir el directorio raíz del proyecto al path
current = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(current)
sys.path.insert(0, parent)

from .simulation import Simulation

# Ruta al archivo donde se escribirá el grid
OUTPUT_PATH = os.path.join(parent, "simulation_output.txt")

def write_grid_to_file(sim: Simulation, turn: int):
    with open(OUTPUT_PATH, "w") as f:
        f.write(f"--- Turn {turn} ---\n\n")
        f.write(sim.grid.str_state)

def main():
    sim = Simulation()

    print("Pulsa ENTER para avanzar al siguiente turno. Ctrl+C para salir.\n")
    
    while True:
        input(f"--- Turno {sim._turn + 1} --- ENTER para continuar ---")
        sim.pass_turn()
        write_grid_to_file(sim, sim._turn)

if __name__ == "__main__":
    main()


# -------------------------------------------------------
# Allow both direct execution and import as module
# -------------------------------------------------------
if __name__ == "__main__":
    main()

"""
from flask import Flask, jsonify

app = Flask(__name__)
sim = Simulation(width=100, height=100, organism_count=150)

@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(sim.get_state())

@app.route("/step", methods=["POST"])
def step():
    sim.step()
    return jsonify(sim.get_state())

if __name__ == "__main__":
    app.run(debug=True)
"""

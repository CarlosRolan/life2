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
        for row in sim.grid.cells:
            line = ""
            for cell in row:
                line += f"{cell.organism.id} " if not cell.is_free else ". "
            f.write(line.rstrip() + "\n")

def main():
    sim = Simulation(width=10, height=10, num_organisms=2)
    turn = 0

    print(f"Simulación iniciada. Visualiza el archivo:\n  {OUTPUT_PATH}")
    print("Pulsa ENTER para avanzar al siguiente turno. Ctrl+C para salir.\n")

    write_grid_to_file(sim, turn)

    while True:
        input(f"--- Turno {turn + 1} --- ENTER para continuar ---")
        sim.next_turn()
        turn += 1
        write_grid_to_file(sim, turn)

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

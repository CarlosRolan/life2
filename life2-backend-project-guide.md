# Life2 Backend — Proyecto (Guía de Configuración y Estructura)

Este documento resume **toda la configuración esencial del proyecto**, incluyendo:

- Cómo está organizada la estructura del proyecto.
- Cómo se debe ejecutar siempre el backend.
- Configuración correcta de VS Code.
- Manejo del entorno virtual.
- Centralización del `__pycache__`.

Es un recordatorio para ti dentro de unos meses, para abrir el proyecto y continuar sin tener que re‑aprender nada.

---

# 📁 1. Estructura del Proyecto

```
/proyecto/
├── life2-back/              # Entorno virtual (venv)
│   ├── bin/
│   ├── lib/
│   ├── pyvenv.cfg
│   └── ...
├── requirements.txt
├── simulation_output.txt
└── src/
    ├── __init__.py          # Marca 'src' como paquete
    ├── main.py              # Entry point del backend
    ├── cmd/
    │   ├── cmd.py
    │   └── __init__.py
    ├── logic/
    │   ├── cellPolicy.py
    │   ├── gridcell.py
    │   ├── grid.py
    │   ├── simulation.py
    │   └── __init__.py
    ├── organism/
    │   ├── organism.py
    │   └── __init__.py
    └── utils/
        └── __init__.py      # Añadido para tratar utils como paquete
```

## 📌 ¿Por qué existen los `__init__.py`?

Estos archivos son necesarios para que Python trate las carpetas como **paquetes importables**.

Gracias a ellos, puedes usar imports como:

```python
from src.logic.grid import Grid
from src.organism.organism import Organism
```

Si faltan, Python no reconoce esas carpetas como paquetes → aparecerían errores como:

```
ModuleNotFoundError: No module named 'src'
```

---

# 🐍 2. Entorno Virtual (`life2-back`)

El entorno virtual se llama:

```
life2-back/
```

Nunca se sube a Git. Se ignora desde `.gitignore`.

Para activarlo:

```bash
source life2-back/bin/activate
```

Desactivarlo:

```bash
deactivate
```

---

# 🧭 3. Ejecución Correcta del Proyecto

IMPORTANTE:  
**Nunca ejecutes `main.py` directamente desde VS Code con “Run Python File”.**

En proyectos con paquetes, eso rompe los imports.

La forma correcta de ejecutar el backend es SIEMPRE:

```bash
python -m src.main
```

Desde la raíz del proyecto (no desde /src).

Esto hace que:

- `src` sea reconocido como paquete.
- Funcione toda la jerarquía de imports.

---

# 🟩 4. Configuración Recomendada de VS Code

En `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run life2 backend",
            "type": "debugpy",
            "request": "launch",

            "module": "src.main",
            "cwd": "${workspaceFolder}",
            "python": "${workspaceFolder}/life2-back/bin/python",

            "env": {
                "PYTHONPYCACHEPREFIX": "${workspaceFolder}/.pycache"
            },

            "console": "integratedTerminal"
        }
    ]
}
```

Esto permite:

- Ejecutar con **F5**.
- Usar SIEMPRE tu venv.
- Ejecución limpia y correcta del paquete `src`.
- Breakpoints, debugging, variables, etc.

---

# 🛠️ 5. Configuración de `settings.json`

Archivo: `.vscode/settings.json`

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/life2-back/bin/python",
    "python.terminal.activateEnvironment": true,

    "terminal.integrated.env.linux": {
        "PYTHONPYCACHEPREFIX": "${workspaceFolder}/.pycache"
    },

    "files.exclude": {
        "**/__pycache__": true
    }
}
```

### Qué hace:

- Selecciona automáticamente tu venv.
- Activa tu venv al abrir la terminal.
- Envía todo el bytecode (`.pyc`) a una carpeta central `.pycache/`.
- Oculta carpetas `__pycache__` por estética.

---

# 📦 6. `.gitignore` recomendado

```
# Entorno virtual
life2-back/

# Caché de Python
__pycache__/
.pycache/

# VS Code
.vscode/

# Bytecode
*.pyc
```

---

# 🎯 7. Resumen Rápido a Futuro

- Ejecuta siempre con **F5** (debug) o `python -m src.main`.
- Nunca uses “Run Python File” del editor.
- Mantén tus `__init__.py`.
- Guarda todo el caché en `.pycache/`.
- Tu entorno virtual está en `life2-back/` (ignorado por Git).
- La raíz del proyecto es la carpeta donde están `src/` y `life2-back/`.

---

# 👍 Fin del documento

Esto es todo lo necesario para reabrir este proyecto y seguir trabajando sin esfuerzo.


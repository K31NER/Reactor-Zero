"""Crea el ejecutable del juego, con las imágenes, la fuente y la música dentro.

Uso:  uv run herramientas/crear_ejecutable.py

El resultado depende del sistema donde se ejecute este script, porque PyInstaller solo
empaqueta para el sistema en el que corre:
  Windows  ->  dist/ReactorZero.exe   (un solo archivo)
  macOS    ->  dist/ReactorZero.app   (una aplicación)

El ejecutable no necesita Python ni uv. Guarda ranking.json en la carpeta donde esté.
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# assets/raw no se incluye: son los originales de la IA y el juego no los usa.
CARPETAS = ["assets/img", "assets/fuentes", "assets/audio"]
EN_MAC = sys.platform == "darwin"

orden = [
    sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed",
    # En macOS una aplicación (.app) ya es una carpeta; ahí no se usa el modo de un solo archivo.
    "--onedir" if EN_MAC else "--onefile",
    "--name", "ReactorZero",
    "--icon", str(RAIZ / "assets" / "img" / "icono.ico"),
]
for carpeta in CARPETAS:
    orden += ["--add-data", f"{RAIZ / carpeta}{';' if sys.platform == 'win32' else ':'}{carpeta}"]
orden.append(str(RAIZ / "main.py"))

subprocess.run(orden, cwd=RAIZ, check=True)
print(f"Listo: {RAIZ / 'dist' / ('ReactorZero.app' if EN_MAC else 'ReactorZero.exe')}")

"""Catálogo de recursos gráficos: qué hojas hay, qué poses tiene cada una y a qué tamaño van.

Lo usan tanto herramientas/procesar_assets.py (para recortar) como el juego (para cargar),
así que el orden de las poses aquí debe ser el mismo que en la hoja, de izquierda a derecha.
"""

import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    # Ejecutable: los recursos van empaquetados dentro y lo que se guarda va junto al .exe.
    RAIZ = Path(sys._MEIPASS)
    DIR_DATOS = Path(sys.executable).resolve().parent
    if sys.platform == "darwin":
        # En macOS no siempre se puede escribir junto a la aplicación; se usa la carpeta del usuario.
        DIR_DATOS = Path.home() / "Library" / "Application Support" / "ReactorZero"
        DIR_DATOS.mkdir(parents=True, exist_ok=True)
else:
    RAIZ = Path(__file__).resolve().parents[2]
    DIR_DATOS = RAIZ
DIR_RAW = RAIZ / "assets" / "raw"
DIR_IMG = RAIZ / "assets" / "img"
DIR_FUENTES = RAIZ / "assets" / "fuentes"
DIR_AUDIO = RAIZ / "assets" / "audio"

ANCHO = 960
ALTO = 540
SUELO_Y = 454  # donde empieza la franja de suelo de los fondos

# Las escenas de la intro son más anchas que la pantalla para poder desplazarlas.
INTRO_ANCHO, INTRO_ALTO = 1056, 594

# Plataformas flotantes: (x, y, ancho, alto). Se pisan por arriba.
PLATAFORMAS = [(120, 330, 220, 12), (620, 330, 220, 12)]

# Píxeles extra que la imagen de brillo tiene a cada lado respecto al sprite.
MARGEN_BRILLO = 14

# "alto" es la altura en pantalla de la primera pose; las demás usan la misma escala.
# "ancla" es el punto del sprite que se apoya en la posición (x, y) al dibujar.
HOJAS = {
    "jugador": {
        "poses": ["quieto", "correr_a", "correr_b", "salto", "derrotado", "celebrando"],
        "alto": 84,
        "ancla": "midbottom",
    },
    "dron_terrestre": {
        "poses": ["caminar_a", "caminar_b", "ataque", "destruido"],
        "alto": 60,
        "ancla": "midbottom",
    },
    "dron_volador": {
        "poses": ["volar_a", "volar_b", "ataque", "destruido"],
        "alto": 46,
        "ancla": "center",
    },
    "meteorito": {
        "poses": ["roca_1", "roca_2", "roca_3"],
        "alto": 52,
        "ancla": "center",
    },
    "reactor": {
        "poses": ["sano", "daniado", "critico", "destruido"],
        "alto": 170,
        "ancla": "midbottom",
        "vidrio": True,  # el modelo pintó el vidrio verde claro; se pasa a cian
    },
}

FONDOS = ["hangar", "exterior", "reactor", "alien"]

PALETA = {
    "fondo": (11, 11, 26),
    "cian": (0, 240, 255),
    "magenta": (255, 43, 214),
    "amarillo": (255, 225, 77),
    "violeta": (122, 92, 255),
    "rojo": (255, 59, 92),
    "texto": (225, 230, 255),
}

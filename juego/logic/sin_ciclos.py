"""Funciones sin ciclos (apartados A y B de la verificación)."""

# Posición horizontal máxima del jugador: ancho de pantalla menos ancho del jugador.
X_MAX = 912

# Velocidad de los drones, en píxeles por segundo.
VELOCIDAD_BASE = 60
VELOCIDAD_INCREMENTO = 15
OLEADA_MAX = 12


def mover_jugador(x: float, direccion: int, velocidad: float) -> float:
    # {P}: direccion in (-1, 0, 1) and velocidad >= 0
    #      and 0 <= x + direccion * velocidad <= X_MAX
    # {Q}: 0 <= x <= X_MAX
    x = x + direccion * velocidad
    return x


def velocidad_oleada(oleada: int) -> int:
    # {P}: 0 <= oleada <= OLEADA_MAX
    # {Q}: v == 60 + 15 * oleada and 60 <= v <= 240
    v = VELOCIDAD_BASE + VELOCIDAD_INCREMENTO * oleada
    return v


def sumar_puntaje(puntaje: int, valor: int, combo: int) -> tuple[int, int]:
    # {P}: puntaje >= 0 and valor > 0 and combo >= 1
    # {Q}: puntaje == puntaje0 + valor * combo0 and combo == combo0 + 1
    ganancia = valor * combo
    puntaje = puntaje + ganancia
    combo = combo + 1
    return puntaje, combo


def aplicar_danio(energia: int, danio: int) -> int:
    # {P}: energia >= 0 and danio >= 0
    # {Q}: r == max(energia - danio, 0)
    if danio >= energia:
        r = 0
    else:
        r = energia - danio
    return r

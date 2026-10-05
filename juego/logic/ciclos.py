"""Funciones con ciclos (apartado C: invariante, variante y terminación).

En los comentarios, n es len() del arreglo.
"""


def contar_activos(enemigos: list) -> int:
    # {P}: enemigos es una lista (n >= 0) y cada elemento tiene el atributo activo
    # {Q}: c == cantidad de k con 0 <= k < n y enemigos[k].activo
    c = 0
    i = 0
    # Invariante: 0 <= i <= n and c == cantidad de k con 0 <= k < i y enemigos[k].activo
    # Variante:   n - i
    while i < len(enemigos):
        if enemigos[i].activo:
            c = c + 1
        i = i + 1
    return c


def indice_maximo_desde(arr: list, inicio: int) -> int:
    # {P}: 0 <= inicio < n
    # {Q}: inicio <= m < n and para todo k (inicio <= k < n -> arr[k] <= arr[m])
    m = inicio
    i = inicio + 1
    # Invariante: inicio <= m < i <= n and para todo k (inicio <= k < i -> arr[k] <= arr[m])
    # Variante:   n - i
    while i < len(arr):
        if arr[i] > arr[m]:
            m = i
        i = i + 1
    return m

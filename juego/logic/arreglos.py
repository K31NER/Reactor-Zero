"""Funciones sobre arreglos (apartado D: índices válidos y ordenamiento).

En los comentarios, n es len() del arreglo y arr0 es el arreglo al entrar a la función.
"""

from juego.logic.ciclos import indice_maximo_desde


def intercambiar(arr: list, i: int, j: int) -> None:
    # {P}: 0 <= i < n and 0 <= j < n
    # {Q}: arr[i] == arr0[j] and arr[j] == arr0[i] y las demás posiciones no cambian
    tmp = arr[i]
    arr[i] = arr[j]
    arr[j] = tmp


def ordenar_ranking(puntajes: list) -> None:
    # {P}: puntajes es una lista de enteros (n >= 0)
    # {Q}: para todo k (0 <= k < n - 1 -> puntajes[k] >= puntajes[k + 1])
    #      y puntajes tiene los mismos elementos que puntajes0
    i = 0
    # Invariante: 0 <= i, los primeros i elementos están ordenados de mayor a menor
    #             y cada uno es >= que todos los elementos desde i en adelante
    # Variante:   n - 1 - i
    while i < len(puntajes) - 1:
        m = indice_maximo_desde(puntajes, i)
        intercambiar(puntajes, i, m)
        i = i + 1

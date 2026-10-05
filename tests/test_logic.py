"""Pruebas de juego/logic. Uso:  uv run pytest"""

from types import SimpleNamespace

import pytest

from juego.logic.arreglos import intercambiar, ordenar_ranking
from juego.logic.ciclos import contar_activos, indice_maximo_desde
from juego.logic.condicionales import (BLOQUEADO, DERRIBADO, ESQUIVA, HERIDO, VOLUMEN_MAX,
                                       ajustar_volumen, clasificar_impacto, mover_seleccion)
from juego.logic.sin_ciclos import (X_MAX, aplicar_danio, mover_jugador, sumar_puntaje,
                                    velocidad_oleada)


def enemigos(*activos):
    return [SimpleNamespace(activo=a) for a in activos]


# --- sin ciclos ---------------------------------------------------------------

@pytest.mark.parametrize("x, direccion, velocidad, esperado", [
    (100, 1, 5, 105),
    (100, -1, 5, 95),
    (100, 0, 5, 100),
    (5, -1, 5, 0),
    (X_MAX - 5, 1, 5, X_MAX),
])
def test_mover_jugador(x, direccion, velocidad, esperado):
    assert mover_jugador(x, direccion, velocidad) == esperado


@pytest.mark.parametrize("oleada, esperado", [(0, 60), (1, 75), (12, 240)])
def test_velocidad_oleada(oleada, esperado):
    assert velocidad_oleada(oleada) == esperado


@pytest.mark.parametrize("puntaje, valor, combo, esperado", [
    (0, 100, 1, (100, 2)),
    (100, 100, 2, (300, 3)),
    (1240, 50, 4, (1440, 5)),
])
def test_sumar_puntaje(puntaje, valor, combo, esperado):
    assert sumar_puntaje(puntaje, valor, combo) == esperado


@pytest.mark.parametrize("energia, danio, esperado", [
    (100, 25, 75),   # rama else
    (10, 25, 0),     # rama if: el caso del bug, no debe quedar en -15
    (25, 25, 0),     # frontera
    (100, 0, 100),
    (0, 0, 0),
])
def test_aplicar_danio(energia, danio, esperado):
    assert aplicar_danio(energia, danio) == esperado


# --- condicional anidado ------------------------------------------------------

@pytest.mark.parametrize("hay_contacto, escudo, vida, danio, esperado", [
    (False, False, 100, 25, ESQUIVA),
    (False, True, 100, 25, ESQUIVA),
    (True, True, 100, 25, BLOQUEADO),
    (True, True, 10, 25, BLOQUEADO),
    (True, False, 10, 25, DERRIBADO),
    (True, False, 25, 25, DERRIBADO),
    (True, False, 100, 25, HERIDO),
])
def test_clasificar_impacto(hay_contacto, escudo, vida, danio, esperado):
    assert clasificar_impacto(hay_contacto, escudo, vida, danio) == esperado


@pytest.mark.parametrize("volumen, cambio, esperado", [
    (6, 1, 7),                       # rama interior: queda dentro del rango
    (6, -1, 5),
    (VOLUMEN_MAX, 1, VOLUMEN_MAX),   # rama del máximo: no pasa de 10
    (0, -1, 0),                      # rama del mínimo: no baja de 0
    (9, 1, VOLUMEN_MAX),             # frontera superior
    (1, -1, 0),                      # frontera inferior
    (5, 0, 5),
])
def test_ajustar_volumen(volumen, cambio, esperado):
    assert ajustar_volumen(volumen, cambio) == esperado


@pytest.mark.parametrize("seleccion, cambio, cantidad, esperado", [
    (0, 1, 3, 1),     # rama interior: baja una opción
    (2, -1, 3, 1),    # rama interior: sube una opción
    (2, 1, 3, 0),     # del final vuelve al principio
    (0, -1, 3, 2),    # del principio salta al final
    (3, 1, 4, 0),
    (0, 1, 1, 0),     # con una sola opción siempre queda en ella
    (0, -1, 1, 0),
])
def test_mover_seleccion(seleccion, cambio, cantidad, esperado):
    assert mover_seleccion(seleccion, cambio, cantidad) == esperado


def test_mover_seleccion_siempre_da_un_indice_valido():
    for cantidad in range(1, 6):
        for seleccion in range(cantidad):
            for cambio in (-1, 1):
                assert 0 <= mover_seleccion(seleccion, cambio, cantidad) < cantidad


# --- ciclos -------------------------------------------------------------------

@pytest.mark.parametrize("activos, esperado", [
    ([], 0),
    ([True], 1),
    ([False], 0),
    ([True, False, True, True], 3),   # la traza de la guía
    ([False, False, False], 0),
])
def test_contar_activos(activos, esperado):
    assert contar_activos(enemigos(*activos)) == esperado


@pytest.mark.parametrize("arr, inicio, esperado", [
    ([7], 0, 0),
    ([3, 9, 5], 0, 1),
    ([9, 3, 5], 1, 2),
    ([3, 5, 9], 2, 2),
    ([4, 8, 8, 1], 0, 1),   # con empate se queda con el primero
])
def test_indice_maximo_desde(arr, inicio, esperado):
    assert indice_maximo_desde(arr, inicio) == esperado


# --- arreglos -----------------------------------------------------------------

def test_intercambiar():
    arr = [10, 20, 30, 40]
    intercambiar(arr, 0, 3)
    assert arr == [40, 20, 30, 10]
    intercambiar(arr, 1, 1)
    assert arr == [40, 20, 30, 10]


def test_intercambiar_indice_invalido():
    # Violar la precondición 0 <= i, j < n produce un error de índice.
    with pytest.raises(IndexError):
        intercambiar([10, 20], 0, 2)


@pytest.mark.parametrize("puntajes", [
    [],
    [500],
    [100, 300, 200],
    [300, 200, 100],
    [100, 200, 300],
    [250, 250, 100, 900, 0],
])
def test_ordenar_ranking(puntajes):
    esperado = sorted(puntajes, reverse=True)
    ordenar_ranking(puntajes)
    assert puntajes == esperado

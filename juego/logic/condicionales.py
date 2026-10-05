"""Funciones con condicional anidado (regla del condicional)."""

ESQUIVA = "ESQUIVA"
BLOQUEADO = "BLOQUEADO"
DERRIBADO = "DERRIBADO"
HERIDO = "HERIDO"

VOLUMEN_MAX = 10


def clasificar_impacto(hay_contacto: bool, escudo: bool, vida: int, danio: int) -> str:
    # {P}: vida > 0 and danio > 0
    # {Q}: (not hay_contacto                               and resultado == ESQUIVA)
    #   or (hay_contacto and escudo                        and resultado == BLOQUEADO)
    #   or (hay_contacto and not escudo and danio >= vida  and resultado == DERRIBADO)
    #   or (hay_contacto and not escudo and danio < vida   and resultado == HERIDO)
    if not hay_contacto:
        resultado = ESQUIVA
    else:
        if escudo:
            resultado = BLOQUEADO
        else:
            if danio >= vida:
                resultado = DERRIBADO
            else:
                resultado = HERIDO
    return resultado


def ajustar_volumen(volumen: int, cambio: int) -> int:
    # {P}: 0 <= volumen <= VOLUMEN_MAX
    # {Q}: 0 <= r <= VOLUMEN_MAX
    #      and (volumen + cambio > VOLUMEN_MAX        and r == VOLUMEN_MAX
    #        or volumen + cambio < 0                  and r == 0
    #        or 0 <= volumen + cambio <= VOLUMEN_MAX  and r == volumen + cambio)
    nuevo = volumen + cambio
    if nuevo > VOLUMEN_MAX:
        r = VOLUMEN_MAX
    else:
        if nuevo < 0:
            r = 0
        else:
            r = nuevo
    return r


def mover_seleccion(seleccion: int, cambio: int, cantidad: int) -> int:
    # Mueve la opción elegida de un menú de `cantidad` opciones, dando la vuelta en los extremos.
    # {P}: cantidad >= 1 and 0 <= seleccion < cantidad and cambio in (-1, 1)
    # {Q}: 0 <= r < cantidad      (r es un índice válido del arreglo de opciones)
    #      and (seleccion + cambio < 0                and r == cantidad - 1
    #        or seleccion + cambio >= cantidad        and r == 0
    #        or 0 <= seleccion + cambio < cantidad    and r == seleccion + cambio)
    nuevo = seleccion + cambio
    if nuevo < 0:
        r = cantidad - 1
    else:
        if nuevo >= cantidad:
            r = 0
        else:
            r = nuevo
    return r

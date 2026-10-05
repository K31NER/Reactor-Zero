"""Guarda en ranking.json el apodo del jugador, el volumen y los mejores puntajes."""

import json

from juego.asset_processor.catalogo import DIR_DATOS
from juego.engine.config import APODO_INICIAL, PUESTOS_RANKING, VOLUMEN_INICIAL
from juego.logic.arreglos import ordenar_ranking
from juego.logic.condicionales import VOLUMEN_MAX

ARCHIVO = DIR_DATOS / "ranking.json"


def cargar(archivo=ARCHIVO):
    """Devuelve {"apodo": str, "volumen": int, "ranking": [(puntaje, apodo), ...]}."""
    datos = {"apodo": APODO_INICIAL, "volumen": VOLUMEN_INICIAL, "ranking": []}
    if archivo.exists():
        try:
            leido = json.loads(archivo.read_text(encoding="utf-8"))
            datos["apodo"] = str(leido["apodo"])
            datos["ranking"] = [(int(p), str(a)) for p, a in leido["ranking"]]
            volumen = leido.get("volumen", VOLUMEN_INICIAL)
            # ajustar_volumen exige 0 <= volumen <= VOLUMEN_MAX; un valor raro en el archivo se descarta.
            if isinstance(volumen, int) and 0 <= volumen <= VOLUMEN_MAX:
                datos["volumen"] = volumen
        except (ValueError, KeyError, TypeError):
            pass  # archivo dañado: se empieza de cero
    return datos


def guardar(datos, archivo=ARCHIVO):
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def registrar(datos, apodo, puntaje):
    """Añade el puntaje, ordena de mayor a menor y deja solo los mejores.

    Cada entrada es la tupla (puntaje, apodo): al comparar tuplas Python mira primero
    el puntaje, así que ordenar_ranking sirve sin cambios.
    """
    entrada = (puntaje, apodo)
    ranking = datos["ranking"]
    ranking.append(entrada)
    ordenar_ranking(ranking)
    del ranking[PUESTOS_RANKING:]
    return entrada

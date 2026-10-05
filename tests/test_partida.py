"""Pruebas de la partida completa, simulada sin abrir ventana. Uso:  uv run pytest"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from juego.asset_processor.catalogo import ALTO, ANCHO, SUELO_Y
from juego.asset_processor.recursos import cargar_fondos, cargar_sprites, crear_estructura
from juego.engine import config as c
from juego.engine import ranking
from juego.engine.partida import CELEBRANDO, FIN, JUGANDO, MITAD_JUGADOR, Controles, Partida
from juego.logic.ciclos import contar_activos

DT = 1 / 60


@pytest.fixture(scope="module")
def recursos():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    yield pantalla, cargar_sprites(), cargar_fondos(), crear_estructura()
    pygame.quit()


def nueva(recursos, semilla=1):
    _, sprites, fondos, estructura = recursos
    return Partida("PRUEBA", sprites, fondos, estructura, semilla=semilla)


def revisar_invariantes(p):
    assert 0 <= p.jugador.vida <= p.jugador.vida_max
    assert 0 <= p.reactor.vida <= p.reactor.vida_max
    assert MITAD_JUGADOR <= p.jugador.x <= ANCHO - MITAD_JUGADOR
    assert p.jugador.y <= SUELO_Y
    assert p.puntaje >= 0 and p.combo >= 1


def test_sin_jugar_el_reactor_cae(recursos):
    """Si el jugador no hace nada, los drones destruyen el reactor y la partida termina."""
    p = nueva(recursos)
    p.jugador.y = 330  # subido a la plataforma, fuera del camino de los drones terrestres
    p.jugador.x = 230
    for _ in range(60 * 240):
        p.actualizar(DT, Controles())
        revisar_invariantes(p)
        if p.estado == FIN:
            break
    assert p.estado == FIN
    assert p.reactor.vida == 0
    assert p.reactor.pose == "destruido"
    assert p.puntaje == 0


def test_disparando_se_supera_la_oleada(recursos):
    """Un jugador que dispara hacia el dron más cercano limpia la primera oleada."""
    p = nueva(recursos)
    pantalla = recursos[0]
    vio_celebracion = False
    for cuadro in range(60 * 120):
        visibles = [d for d in p.enemigos if d.activo and d.espera <= 0]
        controles = Controles(disparar=True)
        if visibles:
            cercano = min(visibles, key=lambda d: abs(d.x - p.jugador.x))
            controles.derecha = cercano.x > p.jugador.x + 60
            controles.izquierda = cercano.x < p.jugador.x - 60
            controles.saltar = cercano.volar
        p.actualizar(DT, controles)
        revisar_invariantes(p)
        if cuadro % 30 == 0:
            p.dibujar(pantalla)
        if p.estado == CELEBRANDO:
            vio_celebracion = True
            assert contar_activos(p.enemigos) == 0
            assert p.jugador.pose in ("celebrando", "salto")
        if p.oleada == 2 and p.estado == JUGANDO:
            break
    assert vio_celebracion
    assert p.oleada == 2
    assert p.sector == 1
    assert p.puntaje > 0


def test_los_bordes_detienen_al_jugador(recursos):
    p = nueva(recursos)
    p.enemigos = []
    for _ in range(60 * 6):
        p.actualizar_jugador(DT, Controles(izquierda=True))
    assert p.jugador.x == MITAD_JUGADOR
    for _ in range(60 * 6):
        p.actualizar_jugador(DT, Controles(derecha=True))
    assert p.jugador.x == ANCHO - MITAD_JUGADOR


def test_el_salto_alcanza_la_plataforma(recursos):
    p = nueva(recursos)
    p.jugador.x = 230
    mas_alto = SUELO_Y
    for i in range(120):
        p.actualizar_jugador(DT, Controles(saltar=i == 0))
        mas_alto = min(mas_alto, p.jugador.y)
    assert mas_alto < 330
    assert p.jugador.y == 330 and p.jugador.en_suelo


def test_el_escudo_evita_golpes_seguidos(recursos):
    p = nueva(recursos)
    dron = p.enemigos[0]
    dron.espera = 0
    dron.x, dron.y = p.jugador.x, SUELO_Y
    assert p.contacto(dron)
    assert p.jugador.vida == c.VIDA_JUGADOR - c.DANIO_DRON
    assert p.jugador.escudo == c.TIEMPO_ESCUDO
    assert p.contacto(dron)
    assert p.jugador.vida == c.VIDA_JUGADOR - c.DANIO_DRON  # bloqueado


def test_ranking_se_ordena_y_se_recorta(tmp_path):
    archivo = tmp_path / "ranking.json"
    datos = ranking.cargar(archivo)
    assert datos == {"apodo": c.APODO_INICIAL, "volumen": c.VOLUMEN_INICIAL, "ranking": []}
    for puntaje in (300, 100, 900, 0, 500, 700, 200):
        ranking.registrar(datos, "ANA", puntaje)
    assert [p for p, _ in datos["ranking"]] == [900, 700, 500, 300, 200]
    ranking.guardar(datos, archivo)
    assert ranking.cargar(archivo) == datos


# --- intro --------------------------------------------------------------------

def imagenes_de_prueba():
    from juego.asset_processor.catalogo import INTRO_ALTO, INTRO_ANCHO
    from juego.engine.historia import ESCENAS
    return [pygame.Surface((INTRO_ANCHO, INTRO_ALTO)) for _ in ESCENAS]


def test_intro_sin_imagenes_nace_terminada(recursos):
    from juego.engine.historia import Intro
    assert Intro(6, imagenes=[]).terminada


def test_intro_recorre_todas_las_escenas(recursos):
    from juego.engine.historia import ESCENAS, Intro
    pantalla = recursos[0]
    intro = Intro(6, imagenes=imagenes_de_prueba(), sonidos=[None] * len(ESCENAS))
    vistas = []
    for _ in range(60 * 120):
        if intro.terminada:
            break
        if not vistas or vistas[-1] != intro.indice:
            vistas.append(intro.indice)
        intro.dibujar(pantalla)
        intro.actualizar(DT)
    assert intro.terminada
    assert vistas == list(range(len(ESCENAS)))


def test_intro_se_puede_saltar(recursos):
    from juego.engine.historia import ESCENAS, Intro
    intro = Intro(6, imagenes=imagenes_de_prueba(), sonidos=[None] * len(ESCENAS))
    assert not intro.terminada
    intro.saltar()
    assert intro.terminada


# --- pausa (a través de main.App, que es lo que recibe las teclas) --------------

@pytest.fixture
def app(recursos, monkeypatch):
    import main
    from juego.engine import ranking as modulo_ranking
    monkeypatch.setattr(modulo_ranking, "guardar", lambda *a, **k: None)
    aplicacion = main.App()
    aplicacion.empezar_partida()
    return aplicacion


def pulsar(aplicacion, tecla):
    aplicacion.evento(pygame.event.Event(pygame.KEYDOWN, key=tecla, unicode=""))


def test_escape_pausa_la_partida_en_vez_de_salir(app):
    for _ in range(30):
        app.actualizar(DT)
    antes = app.partida.tiempo
    pulsar(app, pygame.K_ESCAPE)
    for _ in range(30):
        app.actualizar(DT)
    assert app.estado == "juego" and app.en_pausa
    assert app.partida.tiempo == antes          # la partida no avanza en pausa
    pulsar(app, pygame.K_ESCAPE)
    app.actualizar(DT)
    assert not app.en_pausa and app.partida.tiempo > antes


def test_opciones_del_menu_de_pausa(app):
    vieja = app.partida
    pulsar(app, pygame.K_p)
    pulsar(app, pygame.K_DOWN)
    pulsar(app, pygame.K_RETURN)                # Reiniciar
    assert app.partida is not vieja and app.estado == "juego" and not app.en_pausa
    pulsar(app, pygame.K_p)
    pulsar(app, pygame.K_UP)                    # de la primera salta a la última
    pulsar(app, pygame.K_RETURN)                # Menú principal
    assert app.estado == "menu" and not app.en_pausa

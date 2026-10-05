import pygame

from juego.asset_processor.catalogo import ALTO, ANCHO
from juego.asset_processor.recursos import (cargar_fondos, cargar_icono, cargar_logo,
                                            cargar_sprites, crear_estructura)
from juego.engine import ranking
from juego.engine.historia import Intro
from juego.engine.interfaz import BOTONES, OPCIONES_PAUSA, Interfaz
from juego.engine.musica import Musica
from juego.engine.partida import FIN, Controles, Partida
from juego.entity.jugador import Jugador
from juego.logic.condicionales import ajustar_volumen, mover_seleccion

MENU = "menu"
NOMBRE = "nombre"
RANKING = "ranking"
INTRO = "intro"
JUEGO = "juego"


class App:
    def __init__(self):
        icono = cargar_icono()
        if icono:
            pygame.display.set_icon(icono)  # debe ir antes de crear la ventana
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Reactor Zero")
        self.sprites = cargar_sprites()
        self.fondos = cargar_fondos()
        self.estructura = crear_estructura()
        self.interfaz = Interfaz(self.pantalla, self.fondos, cargar_logo())
        self.datos = ranking.cargar()
        self.musica = Musica(self.datos["volumen"])

        self.estado = MENU
        self.seleccion = 0
        self.escrito = ""
        self.intro = None
        self.partida = None
        self.entrada = None  # la fila del ranking que dejó la última partida
        self.en_pausa = False
        self.seleccion_pausa = 0
        self.tiempo = 0.0
        self.salir = False

    # ---- eventos -----

    def evento(self, e):
        if e.type == pygame.QUIT:
            self.salir = True
        elif self.estado == MENU:
            self.evento_menu(e)
        elif self.estado == NOMBRE:
            self.evento_nombre(e)
        elif self.estado == RANKING:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                self.estado = MENU
        elif self.estado == INTRO:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.intro.saltar()
                self.musica.atenuar(False)
                self.estado = MENU
            elif e.type == pygame.KEYDOWN or (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                self.intro.saltar()
        elif self.estado == JUEGO:
            self.evento_juego(e)

    def evento_juego(self, e):
        if self.partida.estado == FIN:
            # Con la partida terminada no hay pausa: Esc o Enter vuelven al menú.
            listo = self.partida.tiempo_estado >= 1.2
            if e.type == pygame.KEYDOWN and (e.key == pygame.K_ESCAPE or (e.key == pygame.K_RETURN and listo)):
                self.estado = MENU
        elif not self.en_pausa:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_p):
                self.pausar(True)
        elif e.type == pygame.MOUSEMOTION or e.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(OPCIONES_PAUSA)):
                if self.interfaz.rect_pausa(i).collidepoint(e.pos):
                    self.seleccion_pausa = i
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        self.elegir_pausa(i)
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_p):
                self.pausar(False)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.seleccion_pausa = mover_seleccion(self.seleccion_pausa, 1, len(OPCIONES_PAUSA))
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.seleccion_pausa = mover_seleccion(self.seleccion_pausa, -1, len(OPCIONES_PAUSA))
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.elegir_pausa(self.seleccion_pausa)

    def pausar(self, en_pausa):
        self.en_pausa = en_pausa
        self.seleccion_pausa = 0
        self.musica.pausar(en_pausa)

    def elegir_pausa(self, i):
        self.pausar(False)
        if i == 1:
            self.empezar_partida()
        elif i == 2:
            self.estado = MENU

    def evento_menu(self, e):
        if e.type == pygame.MOUSEMOTION or e.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(BOTONES)):
                if self.interfaz.rect_boton(i).collidepoint(e.pos):
                    self.seleccion = i
                    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                        self.elegir(i)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for cambio in (-1, 1):
                    if self.interfaz.rect_volumen(cambio).collidepoint(e.pos):
                        self.cambiar_volumen(cambio)
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_DOWN, pygame.K_s):
                self.seleccion = mover_seleccion(self.seleccion, 1, len(BOTONES))
            elif e.key in (pygame.K_UP, pygame.K_w):
                self.seleccion = mover_seleccion(self.seleccion, -1, len(BOTONES))
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.elegir(self.seleccion)
            elif e.key in (pygame.K_LEFT, pygame.K_a):
                self.cambiar_volumen(-1)
            elif e.key in (pygame.K_RIGHT, pygame.K_d):
                self.cambiar_volumen(1)
            elif e.key == pygame.K_ESCAPE:
                self.salir = True

    def cambiar_volumen(self, cambio):
        self.datos["volumen"] = ajustar_volumen(self.datos["volumen"], cambio)
        self.musica.volumen(self.datos["volumen"])
        ranking.guardar(self.datos)

    def elegir(self, i):
        if i == 0:
            self.intro = Intro(self.datos["volumen"])
            self.musica.atenuar(True)
            self.estado = INTRO
        elif i == 1:
            self.escrito = self.datos["apodo"]
            self.estado = NOMBRE
        elif i == 2:
            self.estado = RANKING
        else:
            self.salir = True

    def empezar_partida(self):
        self.musica.atenuar(False)
        self.partida = Partida(self.datos["apodo"], self.sprites, self.fondos, self.estructura)
        self.entrada = None
        self.en_pausa = False
        self.estado = JUEGO

    def evento_nombre(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if e.key == pygame.K_ESCAPE:
            self.estado = MENU
        elif e.key == pygame.K_BACKSPACE:
            self.escrito = self.escrito[:-1]
        elif e.key == pygame.K_RETURN:
            if Jugador.APODO_MIN <= len(self.escrito) <= Jugador.APODO_MAX:
                self.datos["apodo"] = self.escrito
                ranking.guardar(self.datos)
                self.estado = MENU
        elif e.unicode.isalnum() and len(self.escrito) < Jugador.APODO_MAX:
            self.escrito += e.unicode.upper()

    # --- bucle ------------------------------------------------------------

    def actualizar(self, dt):
        self.tiempo += dt
        if self.estado == INTRO:
            self.intro.actualizar(dt)
            if self.intro.terminada:  # también cuando no hay imágenes de intro
                self.empezar_partida()
        self.musica.poner(self.pista())
        if self.estado != JUEGO or self.en_pausa:
            return
        teclas = pygame.key.get_pressed()
        controles = Controles(
            izquierda=teclas[pygame.K_a] or teclas[pygame.K_LEFT],
            derecha=teclas[pygame.K_d] or teclas[pygame.K_RIGHT],
            saltar=teclas[pygame.K_w] or teclas[pygame.K_UP] or teclas[pygame.K_SPACE],
            disparar=teclas[pygame.K_j],
        )
        self.partida.actualizar(dt, controles)
        if self.partida.estado == FIN and self.entrada is None:
            self.entrada = ranking.registrar(self.datos, self.partida.jugador.apodo,
                                             self.partida.puntaje)
            ranking.guardar(self.datos)

    def pista(self):
        """La música que corresponde a lo que se ve en pantalla."""
        if self.estado != JUEGO:
            return "menu"
        if self.partida.estado == FIN:
            return "fin"
        return "juego"

    def dibujar(self):
        if self.estado == MENU:
            self.interfaz.menu(self.seleccion, self.datos["apodo"], self.datos["volumen"])
        elif self.estado == NOMBRE:
            self.interfaz.nombre(self.escrito, self.tiempo)
        elif self.estado == RANKING:
            self.interfaz.ranking(self.datos["ranking"])
        elif self.estado == INTRO:
            self.intro.dibujar(self.pantalla)
        else:
            self.partida.dibujar(self.pantalla)
            self.interfaz.marcador(self.partida)
            self.interfaz.fin(self.partida, self.datos["ranking"], self.entrada)
            if self.en_pausa:
                self.interfaz.pausa(self.seleccion_pausa)

    def ejecutar(self):
        reloj = pygame.time.Clock()
        while not self.salir:
            for e in pygame.event.get():
                self.evento(e)
            # Si la ventana se congela un momento, no se deja que el tiempo dé un salto.
            self.actualizar(min(reloj.tick(60) / 1000, 1 / 30))
            self.dibujar()
            pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    App().ejecutar()
    pygame.quit()

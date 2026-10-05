"""Todo lo que se dibuja encima de la escena: marcador, menú, apodo, ranking y fin de partida."""

import math

import pygame

from juego.asset_processor.catalogo import ALTO, ANCHO, PALETA, SUELO_Y
from juego.asset_processor.recursos import fuente
from juego.engine import config as c
from juego.engine.partida import CELEBRANDO, FIN, JUGANDO
from juego.entity.jugador import Jugador
from juego.logic.condicionales import VOLUMEN_MAX

BOTONES = ["JUGAR", "CAMBIAR NOMBRE", "MEJORES PUNTAJES", "SALIR"]
OPCIONES_PAUSA = ["CONTINUAR", "REINICIAR", "MENÚ PRINCIPAL"]
SECTORES = ["HANGAR", "EXTERIOR", "SALA DEL REACTOR", "ZONA ALIENÍGENA"]
CONTROLES = "A / D  MOVER      W o ESPACIO  SALTAR      J  DISPARAR      ESC  PAUSA"
Y_VOLUMEN = 494

CENTRO = ANCHO // 2
OSCURO = (11, 11, 26)
PANEL = (20, 20, 51)


class Interfaz:
    def __init__(self, pantalla, fondos, logo):
        self.pantalla = pantalla
        self.logo = logo
        self.fondo_menu = fondos["hangar"].copy()
        velo = pygame.Surface((ANCHO, ALTO))
        velo.set_alpha(150)
        self.fondo_menu.blit(velo, (0, 0))
        self.velo_panel = pygame.Surface((ANCHO, ALTO))
        self.velo_panel.set_alpha(140)

        self.f_grande = fuente(40)
        self.f_titulo = fuente(24)
        self.f_boton = fuente(18)
        self.f_texto = fuente(14)
        self.f_chica = fuente(12, negrita=False)

    # --- piezas -----------------------------------------------------------

    def texto(self, cadena, fnt, color, **ancla):
        img = fnt.render(cadena, True, color)
        self.pantalla.blit(img, img.get_rect(**ancla))

    def rect_boton(self, i):
        rect = pygame.Rect(0, 0, 320, 44)
        rect.midtop = (CENTRO, 262 + i * 56)
        return rect

    def rect_pausa(self, i):
        rect = pygame.Rect(0, 0, 300, 44)
        rect.midtop = (CENTRO, 232 + i * 58)
        return rect

    def rect_volumen(self, cambio):
        """El botón de bajar (cambio -1) o de subir (cambio +1) el volumen."""
        rect = pygame.Rect(0, 0, 26, 24)
        rect.center = (CENTRO + cambio * 126, Y_VOLUMEN)
        return rect

    def control_volumen(self, volumen):
        self.texto("VOLUMEN", self.f_texto, PALETA["texto"], midright=(CENTRO - 152, Y_VOLUMEN))
        raton = pygame.mouse.get_pos()
        for cambio, signo in ((-1, "-"), (1, "+")):
            rect = self.rect_volumen(cambio)
            color = PALETA["amarillo"] if rect.collidepoint(raton) else PALETA["cian"]
            pygame.draw.rect(self.pantalla, OSCURO, rect, border_radius=6)
            pygame.draw.rect(self.pantalla, color, rect, 2, border_radius=6)
            self.texto(signo, self.f_boton, color, center=(rect.centerx, rect.centery - 1))
        for i in range(VOLUMEN_MAX):
            barra = pygame.Rect(CENTRO - 100 + i * 20, Y_VOLUMEN - 9, 16, 18)
            if i < volumen:
                pygame.draw.rect(self.pantalla, PALETA["cian"], barra, border_radius=3)
            else:
                pygame.draw.rect(self.pantalla, PANEL, barra, border_radius=3)
                pygame.draw.rect(self.pantalla, PALETA["violeta"], barra, 1, border_radius=3)

    def boton(self, rect, etiqueta, elegido):
        color = PALETA["amarillo"] if elegido else PALETA["cian"]
        pygame.draw.rect(self.pantalla, PANEL if elegido else OSCURO, rect, border_radius=8)
        pygame.draw.rect(self.pantalla, color, rect, 2, border_radius=8)
        self.texto(etiqueta, self.f_boton, color, center=rect.center)

    def lista_ranking(self, ranking, y, resaltar=None):
        if not ranking:
            self.texto("TODAVÍA NO HAY PUNTAJES", self.f_texto, PALETA["texto"], midtop=(CENTRO, y))
        resaltado = False
        for puesto, entrada in enumerate(ranking, start=1):
            puntaje, apodo = entrada
            color = PALETA["texto"]
            if entrada == resaltar and not resaltado:
                color = PALETA["amarillo"]
                resaltado = True
            fila = y + (puesto - 1) * 30
            self.texto(f"{puesto}.", self.f_boton, color, topright=(CENTRO - 150, fila))
            self.texto(apodo, self.f_boton, color, topleft=(CENTRO - 135, fila))
            self.texto(str(puntaje), self.f_boton, color, topright=(CENTRO + 170, fila))

    # --- pantallas --------------------------------------------------------

    def menu(self, seleccion, apodo, volumen):
        self.pantalla.blit(self.fondo_menu, (0, 0))
        if self.logo:
            self.pantalla.blit(self.logo, self.logo.get_rect(midtop=(CENTRO, 18)),
                               special_flags=pygame.BLEND_RGB_ADD)
        else:
            self.texto("REACTOR ZERO", fuente(56), PALETA["cian"], midtop=(CENTRO, 70))
        self.texto(f"JUGADOR: {apodo}", self.f_texto, PALETA["texto"], midbottom=(CENTRO, 250))
        for i, etiqueta in enumerate(BOTONES):
            self.boton(self.rect_boton(i), etiqueta, i == seleccion)
        self.control_volumen(volumen)
        self.texto(CONTROLES, self.f_chica, PALETA["texto"], midbottom=(CENTRO, ALTO - 12))

    def nombre(self, escrito, tiempo):
        self.pantalla.blit(self.fondo_menu, (0, 0))
        self.texto("CAMBIAR NOMBRE", self.f_grande, PALETA["cian"], midtop=(CENTRO, 110))
        caja = pygame.Rect(0, 0, 420, 56)
        caja.center = (CENTRO, 250)
        pygame.draw.rect(self.pantalla, OSCURO, caja, border_radius=8)
        pygame.draw.rect(self.pantalla, PALETA["amarillo"], caja, 2, border_radius=8)
        cursor = "_" if int(tiempo * 2) % 2 else " "
        self.texto(escrito + cursor, self.f_titulo, PALETA["amarillo"], center=caja.center)

        valido = Jugador.APODO_MIN <= len(escrito) <= Jugador.APODO_MAX
        regla = f"ENTRE {Jugador.APODO_MIN} Y {Jugador.APODO_MAX} LETRAS O NÚMEROS"
        self.texto(regla, self.f_texto, PALETA["texto"] if valido else PALETA["rojo"],
                   midtop=(CENTRO, 300))
        self.texto("ENTER  GUARDAR      ESC  CANCELAR", self.f_chica, PALETA["texto"],
                   midbottom=(CENTRO, ALTO - 12))

    def ranking(self, ranking):
        self.pantalla.blit(self.fondo_menu, (0, 0))
        self.texto("MEJORES PUNTAJES", self.f_grande, PALETA["cian"], midtop=(CENTRO, 90))
        self.lista_ranking(ranking, 200)
        self.texto("ENTER o ESC  VOLVER", self.f_chica, PALETA["texto"], midbottom=(CENTRO, ALTO - 12))

    # --- durante la partida -----------------------------------------------

    def marcador(self, partida):
        self.texto(f"PUNTAJE {partida.puntaje}", self.f_titulo, PALETA["amarillo"], topleft=(20, 14))
        if partida.combo > 1:
            self.texto(f"COMBO x{partida.combo}", self.f_texto, PALETA["magenta"], topleft=(20, 46))
        self.texto(f"OLEADA {partida.oleada}", self.f_titulo, PALETA["texto"], midtop=(CENTRO, 14))
        self.texto(SECTORES[partida.sector], self.f_chica, PALETA["texto"], midtop=(CENTRO, 46))

        # Vidas del jugador: una casilla por cada VIDA_POR_CORAZON.
        j = partida.jugador
        total = math.ceil(j.vida_max / c.VIDA_POR_CORAZON)
        llenas = math.ceil(j.vida / c.VIDA_POR_CORAZON)
        for i in range(total):
            casilla = pygame.Rect(ANCHO - 20 - (total - i) * 30, 18, 22, 22)
            if i < llenas:
                pygame.draw.rect(self.pantalla, PALETA["cian"], casilla, border_radius=5)
            pygame.draw.rect(self.pantalla, PALETA["cian"], casilla, 2, border_radius=5)

        # Energía del reactor.
        r = partida.reactor
        barra = pygame.Rect(0, 0, 120, 10)
        barra.midbottom = (round(r.x), SUELO_Y - 182)
        pygame.draw.rect(self.pantalla, PANEL, barra, border_radius=3)
        lleno = barra.copy()
        lleno.width = round(barra.width * r.vida / r.vida_max)
        color = PALETA["rojo"] if r.pose in ("critico", "destruido") else PALETA["amarillo"]
        pygame.draw.rect(self.pantalla, color, lleno, border_radius=3)
        pygame.draw.rect(self.pantalla, PALETA["violeta"], barra, 1, border_radius=3)

        if partida.estado == JUGANDO and partida.tiempo_estado < c.PAUSA_OLEADA:
            self.texto(f"OLEADA {partida.oleada}", self.f_grande, PALETA["cian"], center=(CENTRO, 150))
            self.texto(SECTORES[partida.sector], self.f_boton, PALETA["texto"], center=(CENTRO, 192))
        elif partida.estado == CELEBRANDO:
            self.texto("OLEADA SUPERADA", self.f_grande, PALETA["amarillo"], center=(CENTRO, 150))

    def pausa(self, seleccion):
        """Menú de pausa, encima de la partida detenida."""
        self.pantalla.blit(self.velo_panel, (0, 0))
        panel = pygame.Rect(0, 0, 400, 330)
        panel.center = (CENTRO, ALTO // 2)
        pygame.draw.rect(self.pantalla, OSCURO, panel, border_radius=12)
        pygame.draw.rect(self.pantalla, PALETA["cian"], panel, 2, border_radius=12)
        self.texto("PAUSA", self.f_grande, PALETA["cian"], midtop=(CENTRO, panel.top + 22))
        for i, etiqueta in enumerate(OPCIONES_PAUSA):
            self.boton(self.rect_pausa(i), etiqueta, i == seleccion)
        self.texto("ESC  CONTINUAR", self.f_chica, PALETA["texto"], midbottom=(CENTRO, panel.bottom - 12))

    def fin(self, partida, ranking, entrada):
        """Panel de fin de partida. Aparece un momento después de perder."""
        if partida.estado != FIN or partida.tiempo_estado < 1.2:
            return
        self.pantalla.blit(self.velo_panel, (0, 0))
        panel = pygame.Rect(0, 0, 480, 380)
        panel.center = (CENTRO, ALTO // 2)
        pygame.draw.rect(self.pantalla, OSCURO, panel, border_radius=12)
        pygame.draw.rect(self.pantalla, PALETA["rojo"], panel, 2, border_radius=12)

        self.texto("FIN DE LA PARTIDA", fuente(30), PALETA["rojo"], midtop=(CENTRO, panel.top + 18))
        if partida.reactor.vida == 0:
            motivo = "EL REACTOR FUE DESTRUIDO"
        else:
            motivo = "EL TÉCNICO FUE DERRIBADO"
        self.texto(motivo, self.f_texto, PALETA["texto"], midtop=(CENTRO, panel.top + 62))
        self.texto(f"PUNTAJE {partida.puntaje}     OLEADA {partida.oleada}", self.f_boton,
                   PALETA["amarillo"], midtop=(CENTRO, panel.top + 92))
        self.texto("MEJORES PUNTAJES", self.f_texto, PALETA["cian"], midtop=(CENTRO, panel.top + 138))
        self.lista_ranking(ranking, panel.top + 166, resaltar=entrada)
        self.texto("ENTER  VOLVER AL MENÚ", self.f_chica, PALETA["texto"],
                   midbottom=(CENTRO, panel.bottom - 14))

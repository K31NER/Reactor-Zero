"""Música de fondo. Si falta un archivo o el equipo no tiene sonido, el juego sigue sin ella."""

import pygame

from juego.asset_processor.catalogo import DIR_AUDIO
from juego.logic.condicionales import VOLUMEN_MAX

# nombre de la pista: (archivo, si se repite en bucle)
PISTAS = {
    "menu": ("The_Quiet_Airlock.mp3", True),
    "juego": ("Defend_the_Core.mp3", True),
    "fin": ("Oxygen_Level_Zero.mp3", False),
}
FUNDIDO_MS = 600
ATENUACION = 0.06  # la música baja a esta fracción mientras habla el narrador (0 la apaga)


class Musica:
    def __init__(self, nivel):
        self.actual = None
        self.atenuada = False
        try:
            pygame.mixer.init()
            self.disponible = True
        except pygame.error:
            self.disponible = False
        self.volumen(nivel)

    def volumen(self, nivel):
        """nivel va de 0 (silencio) a VOLUMEN_MAX."""
        self.nivel = nivel
        if self.disponible:
            factor = ATENUACION if self.atenuada else 1
            pygame.mixer.music.set_volume(nivel / VOLUMEN_MAX * factor)

    def atenuar(self, atenuada):
        """Baja la música (o la devuelve a su volumen) sin cambiar el nivel elegido."""
        self.atenuada = atenuada
        self.volumen(self.nivel)

    def pausar(self, en_pausa):
        """Detiene la música donde va, o la reanuda desde ahí."""
        if not self.disponible:
            return
        if en_pausa:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def poner(self, nombre):
        """Cambia a la pista indicada. No hace nada si ya está sonando."""
        if nombre == self.actual or not self.disponible:
            return
        self.actual = nombre
        archivo, en_bucle = PISTAS[nombre]
        ruta = DIR_AUDIO / archivo
        if not ruta.exists():
            pygame.mixer.music.fadeout(FUNDIDO_MS)
            return
        try:
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play(-1 if en_bucle else 0, fade_ms=FUNDIDO_MS)
        except pygame.error:
            pass

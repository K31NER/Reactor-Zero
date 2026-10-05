"""Carga de imágenes y fuentes, y dibujo de sprites con brillo neón."""

import pygame

from juego.asset_processor.catalogo import (ALTO, ANCHO, DIR_FUENTES, DIR_IMG, FONDOS, HOJAS,
                                            MARGEN_BRILLO, PALETA, PLATAFORMAS, SUELO_Y)


class Pose:
    """Un sprite con su brillo, en las dos orientaciones."""

    def __init__(self, imagen, brillo):
        self.imagen = {False: imagen, True: pygame.transform.flip(imagen, True, False)}
        self.brillo = {False: brillo, True: pygame.transform.flip(brillo, True, False)}
        self.ancho, self.alto = imagen.get_size()


def cargar_sprites():
    """Devuelve sprites[nombre][pose]. Requiere que la ventana ya esté creada."""
    sprites = {}
    for nombre, datos in HOJAS.items():
        sprites[nombre] = {}
        for pose in datos["poses"]:
            imagen = pygame.image.load(DIR_IMG / nombre / f"{pose}.png").convert_alpha()
            brillo = pygame.image.load(DIR_IMG / nombre / f"{pose}_brillo.png").convert()
            sprites[nombre][pose] = Pose(imagen, brillo)
    return sprites


def cargar_fondos():
    return {n: pygame.image.load(DIR_IMG / "fondos" / f"{n}.png").convert() for n in FONDOS}


def cargar_intro(cantidad):
    """Las escenas de la intro, en orden. Lista vacía si falta alguna."""
    rutas = [DIR_IMG / "intro" / f"escena_{i}.jpg" for i in range(1, cantidad + 1)]
    if not all(ruta.exists() for ruta in rutas):
        return []
    return [pygame.image.load(ruta).convert() for ruta in rutas]


def cargar_logo():
    ruta = DIR_IMG / "logo.png"
    return pygame.image.load(ruta).convert() if ruta.exists() else None


def cargar_icono():
    """Icono de la ventana. Se puede cargar antes de crear la ventana."""
    ruta = DIR_IMG / "icono.png"
    return pygame.image.load(ruta) if ruta.exists() else None


def crear_estructura():
    """Suelo y plataformas: una capa opaca y otra de brillo que se suma encima."""
    base = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    luz = pygame.Surface((ANCHO, ALTO))
    pygame.draw.rect(base, (8, 8, 20, 150), (0, SUELO_Y, ANCHO, ALTO - SUELO_Y))
    pygame.draw.line(luz, PALETA["violeta"], (0, SUELO_Y), (ANCHO, SUELO_Y), 2)
    for p in PLATAFORMAS:
        pygame.draw.rect(base, (20, 20, 51, 235), p, border_radius=4)
        pygame.draw.rect(luz, PALETA["violeta"], p, 2, border_radius=4)
    # Difuminado barato: reducir y volver a ampliar.
    chica = pygame.transform.smoothscale(luz, (ANCHO // 6, ALTO // 6))
    halo = pygame.transform.smoothscale(chica, (ANCHO, ALTO))
    luz.blit(halo, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    return base, luz


def dibujar_estructura(pantalla, estructura):
    base, luz = estructura
    pantalla.blit(base, (0, 0))
    pantalla.blit(luz, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def fuente(tam, negrita=True):
    archivo = "Orbitron-Bold.ttf" if negrita else "Orbitron-Regular.ttf"
    return pygame.font.Font(DIR_FUENTES / archivo, tam)


def dibujar(pantalla, nombre, pose, x, y, voltear=False, con_brillo=True):
    """Dibuja la pose apoyando su ancla (pies o centro, según el catálogo) en (x, y)."""
    rect = pose.imagen[voltear].get_rect(**{HOJAS[nombre]["ancla"]: (x, y)})
    if con_brillo:
        pantalla.blit(pose.brillo[voltear], (rect.x - MARGEN_BRILLO, rect.y - MARGEN_BRILLO),
                      special_flags=pygame.BLEND_RGB_ADD)
    pantalla.blit(pose.imagen[voltear], rect)
    return rect


def dibujar_rotado(pantalla, pose, x, y, angulo, con_brillo=True):
    """Dibuja la pose girada alrededor de su centro (para los meteoritos)."""
    if con_brillo:
        brillo = pygame.transform.rotozoom(pose.brillo[False], angulo, 1)
        pantalla.blit(brillo, brillo.get_rect(center=(x, y)), special_flags=pygame.BLEND_RGB_ADD)
    imagen = pygame.transform.rotozoom(pose.imagen[False], angulo, 1)
    pantalla.blit(imagen, imagen.get_rect(center=(x, y)))

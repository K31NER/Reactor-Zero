"""Intro del juego: la historia contada en escenas fijas con narración y subtítulos.

Las imágenes salen de assets/img/intro y la voz, generada con IA, de assets/audio/intro. Si falta alguna
imagen la intro nace terminada, y el juego pasa directo a la partida.
"""

import pygame

from juego.asset_processor.catalogo import ALTO, ANCHO, DIR_AUDIO, PALETA
from juego.asset_processor.recursos import cargar_intro, fuente
from juego.logic.condicionales import VOLUMEN_MAX

# El subtítulo de cada escena. La narración (assets/audio/intro) lee este mismo texto.
ESCENAS = [
    {"texto": "Año 2187. La estación Aurora orbita un mundo helado. "
              "En su interior duermen los últimos doce mil colonos de la Tierra."},
    {"texto": "Un solo corazón los mantiene con vida: el Reactor Zero. "
              "Mientras brille, ellos siguen respirando."},
    {"texto": "Entonces llegó la tormenta. Los meteoritos no traían solo roca: "
              "traían algo vivo, que despertó dentro de las máquinas."},
    {"texto": "Los drones de mantenimiento dejaron de obedecer. "
              "Ahora avanzan, oleada tras oleada, hacia el reactor."},
    {"texto": "La tripulación evacuó. Solo quedó un técnico de guardia: tú. "
              "Si el reactor cae, nadie despierta. Defiéndelo."},
]

PAUSA = 0.9          # silencio al final de cada escena
FUNDIDO = 0.6        # lo que tarda cada escena en aparecer y en irse
ALTO_FRANJA = 100    # franja oscura de los subtítulos
ANCHO_TEXTO = 800


def cargar_narracion():
    """Un sonido por escena; None donde falte el archivo o el equipo no tenga sonido."""
    sonidos = []
    for i in range(1, len(ESCENAS) + 1):
        ruta = DIR_AUDIO / "intro" / f"escena_{i}.wav"
        try:
            sonidos.append(pygame.mixer.Sound(ruta) if ruta.exists() else None)
        except pygame.error:
            sonidos.append(None)
    return sonidos


class Intro:
    def __init__(self, nivel_volumen, imagenes=None, sonidos=None):
        self.imagenes = cargar_intro(len(ESCENAS)) if imagenes is None else imagenes
        self.terminada = len(self.imagenes) != len(ESCENAS)
        self.sonidos = [None] * len(ESCENAS)
        if not self.terminada:
            self.sonidos = cargar_narracion() if sonidos is None else sonidos
        self.volumen = nivel_volumen / VOLUMEN_MAX
        self.f_texto = fuente(20, negrita=False)
        self.f_chica = fuente(12, negrita=False)
        self.franja = pygame.Surface((ANCHO, ALTO_FRANJA))
        self.franja.set_alpha(190)
        self.canal = None
        self.indice = 0
        self.tiempo = 0.0
        if not self.terminada:
            self.empezar_escena()

    def duracion(self, i):
        """Lo que dura la narración de la escena, o un tiempo de lectura si no hay voz."""
        if self.sonidos[i]:
            return self.sonidos[i].get_length() + PAUSA
        return 2.5 + 0.055 * len(ESCENAS[i]["texto"])

    def empezar_escena(self):
        self.tiempo = 0.0
        sonido = self.sonidos[self.indice]
        if sonido:
            sonido.set_volume(self.volumen)
            self.canal = sonido.play()

    def actualizar(self, dt):
        if self.terminada:
            return
        self.tiempo += dt
        if self.tiempo >= self.duracion(self.indice):
            if self.indice + 1 == len(ESCENAS):
                self.terminada = True
            else:
                self.indice += 1
                self.empezar_escena()

    def saltar(self):
        if self.canal:
            self.canal.stop()
        self.terminada = True

    def dibujar(self, pantalla):
        imagen = self.imagenes[self.indice]
        duracion = self.duracion(self.indice)
        avance = min(self.tiempo / duracion, 1)

        # Movimiento de cámara: la imagen es más ancha que la pantalla y se recorre despacio,
        # una escena hacia la derecha y la siguiente hacia la izquierda.
        sobra_x = imagen.get_width() - ANCHO
        sobra_y = imagen.get_height() - ALTO
        if self.indice % 2:
            avance = 1 - avance
        # En vertical se muestra la parte de abajo: ahí están los pies de los personajes.
        pantalla.blit(imagen, (-round(sobra_x * avance), -sobra_y))

        # Fundido desde negro al entrar y hacia negro al salir.
        opacidad = min(self.tiempo / FUNDIDO, (duracion - self.tiempo) / FUNDIDO, 1)
        if opacidad < 1:
            velo = pygame.Surface((ANCHO, ALTO))
            velo.set_alpha(round(255 * (1 - max(opacidad, 0))))
            pantalla.blit(velo, (0, 0))

        pantalla.blit(self.franja, (0, ALTO - ALTO_FRANJA))
        renglones = partir(ESCENAS[self.indice]["texto"], self.f_texto, ANCHO_TEXTO)
        salto = self.f_texto.get_linesize() + 2
        y = ALTO - ALTO_FRANJA / 2 - salto * len(renglones) / 2 - 6
        for renglon in renglones:
            img = self.f_texto.render(renglon, True, PALETA["texto"])
            pantalla.blit(img, img.get_rect(midtop=(ANCHO // 2, round(y))))
            y += salto
        aviso = self.f_chica.render("ESPACIO  SALTAR", True, PALETA["cian"])
        pantalla.blit(aviso, aviso.get_rect(bottomright=(ANCHO - 16, ALTO - 8)))


def partir(texto, fnt, ancho):
    """Divide el texto en renglones que quepan en el ancho dado."""
    renglones = []
    actual = ""
    for palabra in texto.split(" "):
        prueba = palabra if not actual else actual + " " + palabra
        if fnt.size(prueba)[0] <= ancho or not actual:
            actual = prueba
        else:
            renglones.append(actual)
            actual = palabra
    renglones.append(actual)
    return renglones

"""Demo visual de «Reactor Zero»: muestra los personajes y sus poses sobre los escenarios.

No tiene lógica de juego; solo sirve para ver cómo queda el arte.

Uso:  uv run demo.py              abre la ventana
      uv run demo.py --capturas   guarda una imagen de cada página en capturas/ y sale

Teclas:  A/D o flechas izq/der  cambiar de página
         W/S o flechas arr/aba  cambiar de fondo
         F  voltear los sprites     G  activar o quitar el brillo     Esc  salir
"""

import math
import sys

import pygame

from juego.asset_processor.catalogo import ALTO, ANCHO, FONDOS, HOJAS, PALETA, RAIZ, SUELO_Y
from juego.asset_processor.recursos import (cargar_fondos, cargar_logo, cargar_sprites,
                                            crear_estructura, dibujar, dibujar_estructura,
                                            dibujar_rotado, fuente)

TITULOS = {
    "jugador": "JUGADOR",
    "dron_terrestre": "DRON TERRESTRE",
    "dron_volador": "DRON VOLADOR",
    "meteorito": "METEORITO",
    "reactor": "REACTOR",
}
# Altura a la que se muestran las poses de los que no pisan el suelo.
ALTURA_POSES = {"dron_volador": 250, "meteorito": 200}

# Poses cuyo nombre en pantalla lleva letras que el nombre de archivo evita.
ETIQUETAS = {"daniado": "DAÑADO", "critico": "CRÍTICO"}

PAGINAS = list(HOJAS) + ["escena", "menu"]
BOTONES = ["JUGAR", "CAMBIAR NOMBRE", "MEJORES PUNTAJES", "SALIR"]


class Demo:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Reactor Zero - demo de arte")
        self.sprites = cargar_sprites()
        self.fondos = cargar_fondos()
        self.logo = cargar_logo()
        self.estructura = crear_estructura()
        self.f_titulo = fuente(24)
        self.f_texto = fuente(14)
        self.f_chica = fuente(12, negrita=False)
        self.pagina = 0
        self.fondo = 0
        self.voltear = False
        self.brillo = True

    # --- utilidades -------------------------------------------------------

    def texto(self, cadena, fnt, color, **ancla):
        img = fnt.render(cadena, True, color)
        self.pantalla.blit(img, img.get_rect(**ancla))

    def sprite(self, nombre, pose, x, y, voltear=False):
        return dibujar(self.pantalla, nombre, self.sprites[nombre][pose], x, y,
                       voltear, self.brillo)

    def dibujar_escenario(self, oscurecer=0):
        self.pantalla.blit(self.fondos[FONDOS[self.fondo]], (0, 0))
        if oscurecer:
            velo = pygame.Surface((ANCHO, ALTO))
            velo.set_alpha(oscurecer)
            self.pantalla.blit(velo, (0, 0))
            return
        dibujar_estructura(self.pantalla, self.estructura)

    # --- páginas ----------------------------------------------------------

    def pagina_poses(self, nombre):
        self.dibujar_escenario()
        poses = HOJAS[nombre]["poses"]
        paso = ANCHO / len(poses)
        y = ALTURA_POSES.get(nombre, SUELO_Y)
        for i, pose in enumerate(poses):
            x = round(paso * (i + 0.5))
            self.sprite(nombre, pose, x, y, self.voltear)
            etiqueta = ETIQUETAS.get(pose, pose.replace("_", " ").upper())
            self.texto(etiqueta, self.f_texto, PALETA["texto"], midtop=(x, SUELO_Y + 14))
        self.texto(f"{TITULOS[nombre]}  -  {len(poses)} POSES", self.f_titulo,
                   PALETA["cian"], topleft=(20, 16))

    def pagina_escena(self, t):
        """Una pantalla de juego simulada, con movimientos fijos en bucle."""
        self.dibujar_escenario()
        centro = ANCHO // 2
        cuadro = int(t * 8) % 2  # alterna las dos poses de movimiento

        estados = HOJAS["reactor"]["poses"]
        estado = int(t / 3) % len(estados)
        self.sprite("reactor", estados[estado], centro, SUELO_Y)

        # Drones terrestres: caminan hacia el reactor y atacan al llegar.
        for lado, desfase in ((-1, 0.0), (1, 2.5)):
            fase = (t + desfase) % 6
            avance = min(fase / 4.5, 1)
            x = centro + lado * (ANCHO / 2 + 40 - avance * (ANCHO / 2 - 50))
            pose = "ataque" if avance == 1 else ("caminar_a", "caminar_b")[cuadro]
            self.sprite("dron_terrestre", pose, round(x), SUELO_Y, voltear=lado == 1)

        # Dron destruido, quieto en el suelo.
        self.sprite("dron_terrestre", "destruido", 150, SUELO_Y)

        # Drones voladores: llegan por arriba flotando.
        for lado, desfase, altura in ((1, 1.0, 230), (-1, 4.0, 180)):
            fase = (t + desfase) % 7
            x = centro + lado * (ANCHO / 2 + 40 - fase / 7 * (ANCHO / 2 - 20))
            y = altura + 8 * math.sin(t * 4 + desfase)
            pose = "ataque" if fase > 5.5 else ("volar_a", "volar_b")[cuadro]
            self.sprite("dron_volador", pose, round(x), round(y), voltear=lado == 1)

        # Meteoritos: caen girando.
        for i, x in enumerate((230, 560, 800)):
            fase = (t * 0.45 + i * 0.37) % 1
            roca = self.sprites["meteorito"][f"roca_{i + 1}"]
            dibujar_rotado(self.pantalla, roca, x, round(-40 + fase * (SUELO_Y + 20)),
                           t * 120 + i * 90, self.brillo)

        # Jugador: corre de un lado a otro y salta de vez en cuando.
        x = 330 + 90 * math.sin(t * 1.3)
        mira_izquierda = math.cos(t * 1.3) < 0
        salto = (t % 3.2) / 0.7
        if salto < 1:
            self.sprite("jugador", "salto", round(x), round(SUELO_Y - 360 * salto * (1 - salto)),
                        mira_izquierda)
        else:
            self.sprite("jugador", ("correr_a", "correr_b")[cuadro], round(x), SUELO_Y,
                        mira_izquierda)

        # Marcador simulado.
        self.texto("PUNTAJE 1240", self.f_titulo, PALETA["amarillo"], topleft=(20, 16))
        self.texto("OLEADA 3", self.f_titulo, PALETA["texto"], midtop=(centro, 16))
        self.texto("VIDAS 3", self.f_titulo, PALETA["cian"], topright=(ANCHO - 20, 16))
        energia = (1.0, 0.6, 0.25, 0.0)[estado]
        barra = pygame.Rect(0, 0, 120, 10)
        barra.midbottom = (centro, SUELO_Y - 182)
        pygame.draw.rect(self.pantalla, (20, 20, 51), barra, border_radius=3)
        lleno = barra.copy()
        lleno.width = round(barra.width * energia)
        color = (PALETA["amarillo"], PALETA["amarillo"], PALETA["rojo"], PALETA["rojo"])[estado]
        pygame.draw.rect(self.pantalla, color, lleno, border_radius=3)
        pygame.draw.rect(self.pantalla, PALETA["violeta"], barra, 1, border_radius=3)

    def pagina_menu(self):
        self.dibujar_escenario(oscurecer=150)
        centro = ANCHO // 2
        if self.logo:
            self.pantalla.blit(self.logo, self.logo.get_rect(midtop=(centro, 18)),
                               special_flags=pygame.BLEND_RGB_ADD)
        else:
            self.texto("REACTOR ZERO", fuente(56), PALETA["cian"], midtop=(centro, 70))

        raton = pygame.mouse.get_pos()
        for i, etiqueta in enumerate(BOTONES):
            rect = pygame.Rect(0, 0, 320, 44)
            rect.midtop = (centro, 262 + i * 56)
            encima = rect.collidepoint(raton)
            color = PALETA["amarillo"] if encima else PALETA["cian"]
            pygame.draw.rect(self.pantalla, (20, 20, 51) if encima else (11, 11, 26), rect,
                             border_radius=8)
            pygame.draw.rect(self.pantalla, color, rect, 2, border_radius=8)
            self.texto(etiqueta, fuente(18), color, center=rect.center)
        self.texto("JUGADOR: INVITADO", self.f_texto, PALETA["texto"], midbottom=(centro, 250))

    # --- bucle ------------------------------------------------------------

    def dibujar(self, t):
        nombre = PAGINAS[self.pagina]
        if nombre == "escena":
            self.pagina_escena(t)
        elif nombre == "menu":
            self.pagina_menu()
        else:
            self.pagina_poses(nombre)
        pie = (f"PAGINA {self.pagina + 1}/{len(PAGINAS)}   FONDO: {FONDOS[self.fondo].upper()}   "
               f"A/D PAGINA   W/S FONDO   F VOLTEAR   G BRILLO {'SI' if self.brillo else 'NO'}")
        self.texto(pie, self.f_chica, PALETA["texto"], midbottom=(ANCHO // 2, ALTO - 8))

    def tecla(self, k):
        if k in (pygame.K_RIGHT, pygame.K_d):
            self.pagina = (self.pagina + 1) % len(PAGINAS)
        elif k in (pygame.K_LEFT, pygame.K_a):
            self.pagina = (self.pagina - 1) % len(PAGINAS)
        elif k in (pygame.K_DOWN, pygame.K_s):
            self.fondo = (self.fondo + 1) % len(FONDOS)
        elif k in (pygame.K_UP, pygame.K_w):
            self.fondo = (self.fondo - 1) % len(FONDOS)
        elif k == pygame.K_f:
            self.voltear = not self.voltear
        elif k == pygame.K_g:
            self.brillo = not self.brillo

    def ejecutar(self):
        reloj = pygame.time.Clock()
        t = 0.0
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    return
                if e.type == pygame.KEYDOWN:
                    self.tecla(e.key)
            self.dibujar(t)
            pygame.display.flip()
            t += reloj.tick(60) / 1000

    def capturar(self):
        carpeta = RAIZ / "capturas"
        carpeta.mkdir(exist_ok=True)
        for i, nombre in enumerate(PAGINAS):
            self.pagina = i
            self.fondo = i % len(FONDOS)
            self.dibujar(4.3)
            pygame.image.save(self.pantalla, carpeta / f"{i + 1}_{nombre}.png")
        print(f"Capturas guardadas en {carpeta}")


if __name__ == "__main__":
    pygame.init()
    demo = Demo()
    if "--capturas" in sys.argv:
        demo.capturar()
    else:
        demo.ejecutar()
    pygame.quit()

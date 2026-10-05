"""Una partida: mueve las entidades, aplica las reglas y dibuja la escena.

Las reglas que se sustentan en el parcial no están aquí sino en juego.logic; este archivo
solo decide cuándo llamarlas y comprueba antes que se cumpla su precondición.
"""

import math
import random
from dataclasses import dataclass

import pygame

from juego.asset_processor.catalogo import ANCHO, FONDOS, HOJAS, PALETA, PLATAFORMAS, SUELO_Y
from juego.asset_processor.recursos import dibujar_estructura, dibujar_rotado
from juego.engine import config as c
from juego.entity.disparo import Disparo
from juego.entity.dron import Dron
from juego.entity.jugador import Jugador
from juego.entity.meteorito import Meteorito
from juego.entity.reactor import Reactor
from juego.logic.ciclos import contar_activos
from juego.logic.condicionales import DERRIBADO, HERIDO, clasificar_impacto
from juego.logic.sin_ciclos import (OLEADA_MAX, X_MAX, mover_jugador, sumar_puntaje,
                                    velocidad_oleada)

# mover_jugador trabaja con el borde izquierdo del jugador; la entidad guarda su centro.
MITAD_JUGADOR = (ANCHO - X_MAX) / 2

JUGANDO = "jugando"
CELEBRANDO = "celebrando"
FIN = "fin"


@dataclass
class Controles:
    izquierda: bool = False
    derecha: bool = False
    saltar: bool = False
    disparar: bool = False


class Partida:
    def __init__(self, apodo, sprites, fondos, estructura, semilla=None):
        self.sprites = sprites
        self.fondos = fondos
        self.estructura = estructura
        self.azar = random.Random(semilla)
        self.plataformas = [pygame.Rect(p) for p in PLATAFORMAS]
        self.img_disparo = crear_imagen_disparo()

        centro = ANCHO // 2
        self.jugador = Jugador(apodo, c.VIDA_JUGADOR, c.DANIO_DISPARO, centro - 150, SUELO_Y)
        self.reactor = Reactor(c.VIDA_REACTOR, centro, SUELO_Y)
        self.enemigos = []    # arreglo de Dron de la oleada actual
        self.meteoritos = []
        self.disparos = []
        self.particulas = []  # cada una: [x, y, vx, vy, vida, color]

        self.puntaje = 0
        self.combo = 1
        self.oleada = 0
        self.estado = JUGANDO
        self.tiempo = 0.0
        self.tiempo_estado = 0.0
        self.corriendo = False
        self.iniciar_oleada()

    # --- oleadas ----------------------------------------------------------

    def iniciar_oleada(self):
        self.oleada += 1
        self.sector = (self.oleada - 1) % len(FONDOS)
        vuelta = (self.oleada - 1) // len(FONDOS)
        # Sectores: 0 hangar, 1 exterior, 2 sala del reactor, 3 zona alienígena.
        self.hay_meteoritos = vuelta > 0 or self.sector in (1, 3)
        hay_voladores = vuelta > 0 or self.sector in (2, 3)

        # La precondición de velocidad_oleada es 0 <= oleada <= OLEADA_MAX.
        velocidad = velocidad_oleada(min(self.oleada, OLEADA_MAX))
        cantidad = min(c.DRONES_BASE + c.DRONES_POR_OLEADA * self.oleada, c.DRONES_MAX)
        intervalo = max(c.INTERVALO_MIN, c.INTERVALO_BASE - 0.1 * self.oleada)

        self.enemigos = []
        for i in range(cantidad):
            desde_derecha = self.azar.random() < 0.5
            x = ANCHO + 50 if desde_derecha else -50
            if hay_voladores and i % 3 == 2:
                dron = Dron("volador", c.VIDA_VOLADOR, c.DANIO_DRON, x,
                            self.azar.choice(c.ALTURAS_VUELO))
                dron.velocidad = velocidad * c.FACTOR_VOLADOR
            else:
                dron = Dron("terrestre", c.VIDA_TERRESTRE, c.DANIO_DRON, x, SUELO_Y)
                dron.velocidad = velocidad
            dron.espera = c.PAUSA_OLEADA + i * intervalo
            dron.voltear = desde_derecha
            self.enemigos.append(dron)

        self.meteoritos = []
        self.reloj_meteorito = c.PAUSA_OLEADA + self.intervalo_meteorito()
        self.estado = JUGANDO
        self.tiempo_estado = 0.0

    def intervalo_meteorito(self):
        return max(c.INTERVALO_METEORITO_MIN, c.INTERVALO_METEORITO - 0.15 * self.oleada)

    # --- actualización ----------------------------------------------------

    def actualizar(self, dt, controles):
        self.tiempo += dt
        self.tiempo_estado += dt
        if self.estado == FIN:
            controles = Controles()
        elif self.estado == CELEBRANDO:
            controles = Controles()
            if self.tiempo_estado >= c.TIEMPO_CELEBRACION:
                self.iniciar_oleada()

        self.actualizar_jugador(dt, controles)
        self.actualizar_disparos(dt)
        if self.estado == JUGANDO:
            self.actualizar_enemigos(dt)
            self.actualizar_meteoritos(dt)
            self.revisar_final()
        self.actualizar_restos(dt)
        self.actualizar_particulas(dt)
        self.elegir_poses()

    def actualizar_jugador(self, dt, controles):
        j = self.jugador
        j.escudo = max(0.0, j.escudo - dt)
        j.enfriamiento = max(0.0, j.enfriamiento - dt)

        direccion = int(controles.derecha) - int(controles.izquierda)
        self.corriendo = direccion != 0
        if direccion != 0:
            j.voltear = direccion < 0
            paso = c.VELOCIDAD_JUGADOR * dt
            izquierda = j.x - MITAD_JUGADOR
            # mover_jugador exige que el resultado quede dentro de la pantalla.
            if 0 <= izquierda + direccion * paso <= X_MAX:
                izquierda = mover_jugador(izquierda, direccion, paso)
            elif direccion < 0:
                izquierda = 0
            else:
                izquierda = X_MAX
            j.x = izquierda + MITAD_JUGADOR

        if controles.saltar and j.en_suelo:
            j.velocidad_y = -c.IMPULSO_SALTO

        # Gravedad y aterrizaje en el suelo o en una plataforma.
        y_antes = j.y
        j.velocidad_y += c.GRAVEDAD * dt
        j.y += j.velocidad_y * dt
        j.en_suelo = False
        if j.velocidad_y >= 0:
            for p in self.plataformas:
                if p.left - 10 <= j.x <= p.right + 10 and y_antes <= p.top <= j.y:
                    j.y = p.top
                    j.velocidad_y = 0.0
                    j.en_suelo = True
            if j.y >= SUELO_Y:
                j.y = SUELO_Y
                j.velocidad_y = 0.0
                j.en_suelo = True

        if controles.disparar and j.enfriamiento == 0:
            sentido = -1 if j.voltear else 1
            self.disparos.append(Disparo(j.x + sentido * 30, j.y - c.ALTURA_ARMA, sentido, j.danio))
            j.enfriamiento = c.TIEMPO_ENTRE_DISPAROS

    def actualizar_disparos(self, dt):
        for disparo in self.disparos:
            disparo.avanzar(dt)
            if disparo.x < -20 or disparo.x > ANCHO + 20:
                disparo.activo = False
                continue
            for dron in self.enemigos:
                if dron.activo and dron.espera <= 0 and self.caja(dron).collidepoint(disparo.x, disparo.y):
                    disparo.activo = False
                    dron.recibir_danio(disparo.danio)
                    self.chispas(disparo.x, disparo.y, PALETA["cian"], 5)
                    if not dron.activo:
                        self.dron_destruido(dron)
                    break
        self.disparos = [d for d in self.disparos if d.activo]

    def dron_destruido(self, dron):
        valor = c.VALOR_VOLADOR if dron.volar else c.VALOR_TERRESTRE
        self.puntaje, self.combo = sumar_puntaje(self.puntaje, valor, self.combo)
        self.combo = min(self.combo, c.COMBO_MAX)
        dron.pose = "destruido"
        dron.tiempo_destruido = c.TIEMPO_RESTOS
        self.chispas(dron.x, self.caja(dron).centery, PALETA["magenta"], 16)

    def actualizar_enemigos(self, dt):
        centro = self.reactor.x
        cuadro = int(self.tiempo * 8) % 2
        for dron in self.enemigos:
            if not dron.activo:
                continue
            if dron.espera > 0:
                dron.espera -= dt
                continue

            sentido = 1 if dron.x < centro else -1
            llego = False
            if dron.volar:
                objetivo_y = SUELO_Y - 120
                if abs(dron.x - centro) > c.DISTANCIA_PICADA:
                    dron.x += sentido * dron.velocidad * dt
                    dron.y = dron.altura + 6 * math.sin(self.tiempo * 4 + dron.altura)
                    dron.pose = ("volar_a", "volar_b")[cuadro]
                else:
                    dx, dy = centro - dron.x, objetivo_y - dron.y
                    distancia = math.hypot(dx, dy)
                    paso = dron.velocidad * dt
                    if distancia <= paso + 12:
                        llego = True
                    else:
                        dron.x += dx / distancia * paso
                        dron.y += dy / distancia * paso
                    dron.pose = "ataque"
            else:
                if abs(dron.x - centro) > c.DISTANCIA_ATAQUE:
                    dron.x += sentido * dron.velocidad * dt
                    dron.pose = ("caminar_a", "caminar_b")[cuadro]
                else:
                    llego = True
                    dron.pose = "ataque"

            if llego:
                dron.tiempo_ataque += dt
                if dron.tiempo_ataque >= c.TIEMPO_ATAQUE:
                    dron.atacar(self.reactor)
                    dron.recibir_danio(dron.vida)  # se destruye al golpear
                    self.chispas(dron.x, self.caja(dron).centery, PALETA["rojo"], 18)
            else:
                self.contacto(dron)

    def actualizar_meteoritos(self, dt):
        if self.hay_meteoritos:
            self.reloj_meteorito -= dt
            if self.reloj_meteorito <= 0:
                self.reloj_meteorito = self.intervalo_meteorito()
                self.crear_meteorito()

        siguen = []
        for m in self.meteoritos:
            if m.espera > 0:
                m.espera -= dt
                siguen.append(m)
                continue
            base_antes = m.y + c.RADIO_METEORITO
            m.y += m.velocidad * dt
            m.angulo += 160 * dt
            base = m.y + c.RADIO_METEORITO
            choca = base >= SUELO_Y
            for p in self.plataformas:
                if p.left <= m.x <= p.right and base_antes <= p.top <= base:
                    choca = True
            if self.contacto(m):
                choca = True
            if choca:
                self.chispas(m.x, min(base, SUELO_Y), PALETA["rojo"], 14)
            else:
                siguen.append(m)
        self.meteoritos = siguen

    def crear_meteorito(self):
        # No caen sobre el reactor: solo amenazan al jugador.
        x = self.azar.uniform(40, ANCHO - 40)
        while abs(x - self.reactor.x) < 80:
            x = self.azar.uniform(40, ANCHO - 40)
        m = Meteorito(self.azar.randint(1, Meteorito.ROCAS), c.DANIO_METEORITO, x, -40)
        m.velocidad = c.VELOCIDAD_METEORITO + 10 * self.oleada
        m.espera = c.TIEMPO_AVISO
        self.meteoritos.append(m)

    def contacto(self, amenaza):
        """Resuelve el choque entre el jugador y un dron o meteorito. Devuelve si se tocaron."""
        j = self.jugador
        if j.vida == 0:  # clasificar_impacto exige vida > 0
            return False
        hay_contacto = self.caja(j).colliderect(self.caja(amenaza))
        resultado = clasificar_impacto(hay_contacto, j.escudo > 0, j.vida, amenaza.danio)
        if resultado in (HERIDO, DERRIBADO):
            amenaza.atacar(j)
            j.escudo = c.TIEMPO_ESCUDO
            self.combo = 1
            self.chispas(j.x, j.y - 40, PALETA["rojo"], 12)
        return hay_contacto

    def revisar_final(self):
        if self.reactor.vida == 0 or self.jugador.vida == 0:
            self.estado = FIN
            self.tiempo_estado = 0.0
            if self.reactor.vida == 0:
                self.chispas(self.reactor.x, SUELO_Y - 90, PALETA["amarillo"], 40)
        elif contar_activos(self.enemigos) == 0:
            self.estado = CELEBRANDO
            self.tiempo_estado = 0.0
            for m in self.meteoritos:
                if m.espera <= 0:
                    self.chispas(m.x, m.y, PALETA["rojo"], 10)
            self.meteoritos = []

    def actualizar_restos(self, dt):
        for dron in self.enemigos:
            if not dron.activo and dron.tiempo_destruido > 0:
                dron.tiempo_destruido -= dt
                if dron.volar and dron.y < SUELO_Y - 20:
                    dron.y = min(SUELO_Y - 20, dron.y + 320 * dt)

    def actualizar_particulas(self, dt):
        for p in self.particulas:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 500 * dt
            p[4] -= dt
        self.particulas = [p for p in self.particulas if p[4] > 0]

    def chispas(self, x, y, color, cantidad):
        for _ in range(cantidad):
            angulo = self.azar.uniform(0, math.tau)
            rapidez = self.azar.uniform(60, 260)
            self.particulas.append([x, y, math.cos(angulo) * rapidez, math.sin(angulo) * rapidez - 80,
                                    self.azar.uniform(0.25, 0.6), color])

    def elegir_poses(self):
        j = self.jugador
        if self.estado == FIN:
            j.pose = "derrotado" if j.en_suelo else "salto"
        elif not j.en_suelo:
            j.pose = "salto"
        elif self.estado == CELEBRANDO:
            j.pose = "celebrando"
        elif self.corriendo:
            j.pose = ("correr_a", "correr_b")[int(self.tiempo * 10) % 2]
        else:
            j.pose = "quieto"

        r = self.reactor
        if r.vida == 0:
            r.pose = "destruido"
        elif r.vida * 3 <= r.vida_max:
            r.pose = "critico"
        elif r.vida * 3 <= r.vida_max * 2:
            r.pose = "daniado"
        else:
            r.pose = "sano"

    def caja(self, entidad):
        """Rectángulo de choque: algo más pequeño que el dibujo, para que sea justo."""
        imagen = self.sprites[entidad.nombre][entidad.pose].imagen[False]
        rect = imagen.get_rect(**{HOJAS[entidad.nombre]["ancla"]: (round(entidad.x), round(entidad.y))})
        return rect.inflate(-rect.width * 0.3, -rect.height * 0.2)

    # --- dibujo -----------------------------------------------------------

    def dibujar(self, pantalla):
        pantalla.blit(self.fondos[FONDOS[self.sector]], (0, 0))
        dibujar_estructura(pantalla, self.estructura)
        self.reactor.dibujar(pantalla, self.sprites)

        for dron in self.enemigos:
            if dron.activo:
                if dron.espera <= 0:
                    dron.dibujar(pantalla, self.sprites)
            elif dron.tiempo_destruido > 0.3 or int(dron.tiempo_destruido * 20) % 2:
                dron.dibujar(pantalla, self.sprites)  # los restos parpadean antes de irse

        j = self.jugador
        if j.escudo == 0 or int(self.tiempo * 14) % 2:
            j.dibujar(pantalla, self.sprites)

        for d in self.disparos:
            pantalla.blit(self.img_disparo, self.img_disparo.get_rect(center=(round(d.x), round(d.y))),
                          special_flags=pygame.BLEND_RGB_ADD)

        for m in self.meteoritos:
            if m.espera > 0:
                if int(self.tiempo * 10) % 2:
                    x = round(m.x)
                    pygame.draw.polygon(pantalla, PALETA["rojo"], [(x - 9, 6), (x + 9, 6), (x, 22)])
            else:
                dibujar_rotado(pantalla, self.sprites["meteorito"][m.pose], round(m.x), round(m.y),
                               m.angulo)

        for x, y, _, _, vida, color in self.particulas:
            pygame.draw.circle(pantalla, color, (round(x), round(y)), max(1, round(vida * 7)))


def crear_imagen_disparo():
    """Trazo cian con resplandor, para dibujarlo sumando colores."""
    img = pygame.Surface((44, 20))
    pygame.draw.line(img, PALETA["cian"], (10, 10), (34, 10), 4)
    chica = pygame.transform.smoothscale(img, (11, 5))
    halo = pygame.transform.smoothscale(chica, (44, 20))
    img.blit(halo, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    pygame.draw.line(img, (255, 255, 255), (14, 10), (30, 10), 2)
    return img

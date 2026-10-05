"""Valores de la partida. Cambiarlos ajusta la dificultad sin tocar el código."""

# Jugador
VIDA_JUGADOR = 300
DANIO_DISPARO = 50
VELOCIDAD_JUGADOR = 300     # pixeles por segundo
IMPULSO_SALTO = 700         # pixeles por segundo, hacia arriba
GRAVEDAD = 1800             # pixeles por segundo al cuadrado
TIEMPO_ENTRE_DISPAROS = 0.28
TIEMPO_ESCUDO = 1.5         # invulnerabilidad tras recibir un golpe
ALTURA_ARMA = 40            # altura del disparo sobre los pies
VIDA_POR_CORAZON = 100      # el marcador muestra vida / este valor
COMBO_MAX = 9               # el multiplicador de puntos no pasa de aquí

# Reactor
VIDA_REACTOR = 1000
DISTANCIA_ATAQUE = 82       # a esta distancia del centro el dron terrestre se detiene y ataca

# Drones
VIDA_TERRESTRE = 100
VIDA_VOLADOR = 50
DANIO_DRON = 100
VALOR_TERRESTRE = 100       # puntos por destruirlo, antes de multiplicar por el combo
VALOR_VOLADOR = 150
FACTOR_VOLADOR = 1.2        # los voladores van algo más rápido
ALTURAS_VUELO = (240, 285)
DISTANCIA_PICADA = 170      # a esta distancia horizontal el volador se lanza al reactor
TIEMPO_ATAQUE = 0.6         # lo que tarda en golpear al reactor una vez llega
TIEMPO_RESTOS = 0.9         # lo que se ven los restos de un dron destruido

# Oleadas
DRONES_BASE = 4
DRONES_POR_OLEADA = 2
DRONES_MAX = 20
INTERVALO_BASE = 2.0        # segundos entre la entrada de un dron y el siguiente
INTERVALO_MIN = 0.7
PAUSA_OLEADA = 2.0          # segundos de respiro al empezar cada oleada
TIEMPO_CELEBRACION = 2.5

# Meteoritos
DANIO_METEORITO = 100
VELOCIDAD_METEORITO = 240
TIEMPO_AVISO = 0.9          # la marca roja aparece este tiempo antes de que caiga
INTERVALO_METEORITO = 3.0
INTERVALO_METEORITO_MIN = 1.2
RADIO_METEORITO = 22

# Ranking
PUESTOS_RANKING = 5
APODO_INICIAL = "Z3R0"

# Sonido
VOLUMEN_INICIAL = 5         # de 0 a VOLUMEN_MAX (10)

from juego.entity.base import Entidad

class Jugador(Entidad):
    # Delimitadores del apodo que se guarda en el ranking
    APODO_MAX = 15
    APODO_MIN = 3

    POSE_INICIAL = "quieto"

    def __init__(self, apodo: str, vida: int, danio: int, x: float, y: float):
        super().__init__("jugador", vida, danio, x, y)

        if len(apodo) > self.APODO_MAX:
            raise ValueError(f"El apodo no puede tener mas de {self.APODO_MAX} caracteres")
        if len(apodo) < self.APODO_MIN:
            raise ValueError(f"El apodo debe tener al menos {self.APODO_MIN} caracteres")
        self.apodo = apodo

        # Estado de movimiento (lo actualiza el motor)
        self.velocidad_y = 0.0     # pixeles por segundo; negativa cuando sube
        self.en_suelo = True
        self.escudo = 0.0          # segundos de invulnerabilidad que quedan tras un golpe
        self.enfriamiento = 0.0    # segundos que faltan para poder disparar de nuevo

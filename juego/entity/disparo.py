class Disparo:
    """Proyectil del jugador. No es una Entidad: no tiene vida ni hoja de sprites."""

    VELOCIDAD = 720  # pixeles por segundo

    def __init__(self, x: float, y: float, direccion: int, danio: int):
        self.x = x
        self.y = y
        self.direccion = direccion  # 1 hacia la derecha, -1 hacia la izquierda
        self.danio = danio
        self.activo = True

    def avanzar(self, dt: float):
        self.x = self.x + self.direccion * self.VELOCIDAD * dt

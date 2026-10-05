from juego.entity.base import Entidad

class Meteorito(Entidad):
    # El meteorito no se puede destruir: su vida es un valor fijo que nunca cambia
    VIDA_INICIAL_MAX = 1
    VIDA_INICIAL_MIN = 1

    ROCAS = 3

    def __init__(self, roca: int, danio: int, x: float, y: float):
        if roca < 1 or roca > self.ROCAS:
            raise ValueError(f"La roca debe estar entre 1 y {self.ROCAS}")
        super().__init__("meteorito", 1, danio, x, y)

        self.pose = f"roca_{roca}"

        # Estado de movimiento (lo actualiza el motor)
        self.velocidad = 0.0   # pixeles por segundo, hacia abajo
        self.espera = 0.0      # segundos de aviso antes de empezar a caer
        self.angulo = 0.0      # giro del dibujo, en grados

    def recibir_danio(self, danio: int):
        pass # Como no puede recibir daño se sobre escribe el meto sin ejecutar logica

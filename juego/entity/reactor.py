from juego.entity.base import Entidad

class Reactor(Entidad):
    # El reactor no hace daño
    DANIO_MAX = 0
    DANIO_MIN = 0

    POSE_INICIAL = "sano"

    def __init__(self, vida: int, x: float, y: float):
        super().__init__("reactor", vida, 0, x, y)

from juego.entity.base import Entidad

class Dron(Entidad):
    TIPOS = ("terrestre", "volador")

    def __init__(self, tipo: str, vida: int, danio: int, x: float, y: float):
        if tipo not in self.TIPOS:
            raise ValueError(f"El tipo de dron debe ser uno de {self.TIPOS}")
        super().__init__(f"dron_{tipo}", vida, danio, x, y)

        self.tipo = tipo
        self.volar = tipo == "volador"
        self.pose = "volar_a" if self.volar else "caminar_a"

        # Estado de movimiento (lo actualiza el motor)
        self.velocidad = 0.0          # pixeles por segundo
        self.espera = 0.0             # segundos que faltan para que entre a la pantalla
        self.altura = y               # altura de vuelo, solo para los voladores
        self.tiempo_ataque = 0.0      # segundos que lleva atacando al reactor
        self.tiempo_destruido = 0.0   # segundos que quedan mostrando los restos

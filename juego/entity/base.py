from juego.asset_processor.catalogo import HOJAS
from juego.logic.sin_ciclos import aplicar_danio
from juego.asset_processor.recursos import dibujar

def validar_rango(etiqueta: str, valor: int, minimo: int, maximo: int):
    if valor > maximo:
        raise ValueError(f"{etiqueta} no puede ser mayor a {maximo}")
    if valor < minimo:
        raise ValueError(f"{etiqueta} no puede ser menor a {minimo}")


class Entidad:
    # Delimitadores de los valores con los que se crea la entidad.
    # Durante el juego la vida baja hasta 0; estos límites solo aplican al crearla.
    VIDA_INICIAL_MAX = 1000
    VIDA_INICIAL_MIN = 50
    DANIO_MAX = 500
    DANIO_MIN = 25

    POSE_INICIAL = None

    def __init__(self, nombre: str, vida: int, danio: int, x: float, y: float):
        # Posicion
        self.x = x
        self.y = y

        # Acciones
        self.activo = True
        self.voltear = False
        self.pose = self.POSE_INICIAL

        # Parametros validados
        if nombre not in HOJAS:
            raise ValueError(f"No existe la hoja de sprites '{nombre}'")
        self.nombre = nombre

        validar_rango("La vida", vida, self.VIDA_INICIAL_MIN, self.VIDA_INICIAL_MAX)
        self.vida = vida
        self.vida_max = vida

        validar_rango("El daño", danio, self.DANIO_MIN, self.DANIO_MAX)
        self.danio = danio

    def recibir_danio(self, danio: int):
        """ Recibe daño"""
        if danio < 0:
            raise ValueError("El daño recibido no puede ser negativo")
        self.vida = aplicar_danio(self.vida, danio)
        if self.vida == 0:
            self.activo = False

    def atacar(self, objetivo: "Entidad"):
        """ Realiza daño a otra entidad """
        objetivo.recibir_danio(self.danio)

    def dibujar(self, pantalla, sprites, con_brillo: bool = True):
        """ Dibuja las entidades en pantalla y modifica sus poses o estados segun la accion """
        return dibujar(pantalla, self.nombre, sprites[self.nombre][self.pose],
                    round(self.x), round(self.y), self.voltear, con_brillo)

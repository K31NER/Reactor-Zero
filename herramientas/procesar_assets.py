"""Convierte las imágenes de assets/raw en los recursos que carga el juego (assets/img).

Para cada hoja de sprites: quita el fondo verde, separa las poses, las reduce al tamaño
del juego y genera su imagen de brillo. Los fondos y el logo solo se recortan y reducen.

Uso:  uv run herramientas/procesar_assets.py
Necesita Pillow y numpy (el juego en sí solo necesita pygame).
"""

import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from juego.asset_processor.catalogo import (ALTO, ANCHO, DIR_FUENTES, DIR_IMG, DIR_RAW, FONDOS,
                                            HOJAS, INTRO_ALTO, INTRO_ANCHO, MARGEN_BRILLO, RAIZ)

# "Verdor" de un píxel = g - max(r, b). El fondo ronda 240; el vidrio del reactor, 60-160.
VERDOR_SOLIDO = 140  # por debajo, el píxel es del personaje
VERDOR_FONDO = 200   # por encima, es fondo

HUECO_MIN = 6        # columnas vacías que separan dos poses
ANCHO_MIN = 30       # una "pose" más angosta que esto es ruido
BRILLO_UMBRAL = 120  # solo los píxeles más claros que esto emiten brillo
BRILLO_RADIO = 5


def quitar_verde(img, vidrio=False):
    """Devuelve la imagen en RGBA con el fondo verde transparente."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    verdor = g - np.maximum(r, b)
    alfa = np.clip((VERDOR_FONDO - verdor) / (VERDOR_FONDO - VERDOR_SOLIDO), 0, 1)

    if vidrio:
        es_vidrio = (verdor > 50) & (np.minimum(r, b) > 60) & (alfa > 0)
        b = np.where(es_vidrio, g, b)
    # Quita el tinte verde que queda en los bordes.
    g = np.minimum(g, np.maximum(r, b))

    rgba = np.dstack([r, g, b, alfa * 255]).astype(np.uint8)
    salida = Image.fromarray(rgba, "RGBA")
    # Come un píxel del borde, que es donde se mezclan personaje y fondo.
    salida.putalpha(salida.getchannel("A").filter(ImageFilter.MinFilter(3)))
    return salida


def tramos(ocupado, hueco_min, largo_min):
    """Lista de (inicio, fin) de los tramos seguidos de True, uniendo huecos pequeños."""
    resultado = []
    inicio = None
    vacios = 0
    for i, lleno in enumerate(ocupado):
        if lleno:
            if inicio is None:
                inicio = i
            vacios = 0
        elif inicio is not None:
            vacios += 1
            if vacios >= hueco_min:
                resultado.append((inicio, i - vacios + 1))
                inicio = None
    if inicio is not None:
        resultado.append((inicio, len(ocupado) - vacios))
    return [(a, b) for a, b in resultado if b - a >= largo_min]


def separar_poses(rgba):
    """Recorta cada pose de la hoja, de izquierda a derecha."""
    solido = np.asarray(rgba.getchannel("A")) > 128
    poses = []
    for x0, x1 in tramos(solido.sum(axis=0) >= 2, HUECO_MIN, ANCHO_MIN):
        filas = tramos(solido[:, x0:x1].sum(axis=1) >= 2, 12, ANCHO_MIN)
        y0, y1 = max(filas, key=lambda f: f[1] - f[0])
        poses.append(rgba.crop((x0, y0, x1, y1)))
    return poses


def reducir(rgba, escala):
    """Reduce con alfa premultiplicado, para que el borde no se oscurezca."""
    tam = (max(1, round(rgba.width * escala)), max(1, round(rgba.height * escala)))
    return rgba.convert("RGBa").resize(tam, Image.LANCZOS).convert("RGBA")


def crear_brillo(sprite):
    """Imagen RGB sobre negro con el resplandor del sprite; se dibuja sumando colores."""
    a = np.asarray(sprite).astype(np.float32)
    rgb = a[..., :3] * (a[..., 3:] / 255)
    rgb[rgb.max(axis=2) < BRILLO_UMBRAL] = 0
    m = MARGEN_BRILLO
    lienzo = np.zeros((sprite.height + 2 * m, sprite.width + 2 * m, 3), np.uint8)
    lienzo[m:-m, m:-m] = rgb.astype(np.uint8)
    img = Image.fromarray(lienzo, "RGB")
    ancho = img.filter(ImageFilter.GaussianBlur(BRILLO_RADIO))
    fino = img.filter(ImageFilter.GaussianBlur(BRILLO_RADIO / 3))
    suma = np.asarray(ancho).astype(np.float32) * 0.9 + np.asarray(fino) * 0.35
    return Image.fromarray(np.clip(suma, 0, 255).astype(np.uint8), "RGB")


def procesar_hoja(nombre, datos):
    hoja = quitar_verde(Image.open(DIR_RAW / f"{nombre}.png"), datos.get("vidrio", False))
    poses = separar_poses(hoja)
    esperadas = datos["poses"]
    if len(poses) != len(esperadas):
        raise SystemExit(f"{nombre}.png: se esperaban {len(esperadas)} poses y se "
                         f"detectaron {len(poses)}. Revisa que no se toquen entre sí.")

    escala = datos["alto"] / poses[0].height
    carpeta = DIR_IMG / nombre
    carpeta.mkdir(parents=True, exist_ok=True)
    for i, (pose, recorte) in enumerate(zip(esperadas, poses), start=1):
        suelta = DIR_RAW / f"{nombre}_{i}.png"  # reemplazo de una pose suelta
        if suelta.exists():
            recorte = separar_poses(quitar_verde(Image.open(suelta), datos.get("vidrio", False)))[0]
        sprite = reducir(recorte, escala)
        sprite.save(carpeta / f"{pose}.png")
        crear_brillo(sprite).save(carpeta / f"{pose}_brillo.png")
        print(f"  {nombre}/{pose}.png  {sprite.width}x{sprite.height}")


def recortar_a_16_9(img):
    alto = round(img.width * ALTO / ANCHO)
    if alto <= img.height:
        y = (img.height - alto) // 2
        return img.crop((0, y, img.width, y + alto))
    ancho = round(img.height * ANCHO / ALTO)
    x = (img.width - ancho) // 2
    return img.crop((x, 0, x + ancho, img.height))


def procesar_fondos():
    carpeta = DIR_IMG / "fondos"
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre in FONDOS:
        img = Image.open(DIR_RAW / f"fondo_{nombre}.png").convert("RGB")
        recortar_a_16_9(img).resize((ANCHO, ALTO), Image.LANCZOS).save(carpeta / f"{nombre}.png")
        print(f"  fondos/{nombre}.png")


def procesar_logo():
    origen = DIR_RAW / "logo.png"
    if not origen.exists():
        return
    img = Image.open(origen).convert("RGB")
    a = np.asarray(img)
    a = np.where(a.max(axis=2, keepdims=True) < 18, 0, a).astype(np.uint8)  # negro puro
    img = Image.fromarray(a, "RGB")
    caja = img.getbbox()
    margen = 20
    img = img.crop((max(0, caja[0] - margen), max(0, caja[1] - margen),
                    min(img.width, caja[2] + margen), min(img.height, caja[3] + margen)))
    ancho = 520
    img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS).save(DIR_IMG / "logo.png")
    print("  logo.png")


def procesar_intro():
    """Escenas de la intro: se recortan a 16:9 y quedan algo más grandes que la pantalla."""
    origenes = sorted((DIR_RAW / "intro").glob("escena_*.png"))
    if not origenes:
        return
    carpeta = DIR_IMG / "intro"
    carpeta.mkdir(parents=True, exist_ok=True)
    for origen in origenes:
        img = recortar_a_16_9(Image.open(origen).convert("RGB"))
        img.resize((INTRO_ANCHO, INTRO_ALTO), Image.LANCZOS).save(carpeta / f"{origen.stem}.jpg", quality=90)
        print(f"  intro/{origen.stem}.jpg")


def procesar_icono():
    """Icono de la ventana (PNG) y del ejecutable (ICO con varios tamaños)."""
    origen = DIR_RAW / "icono.png"
    if not origen.exists():
        return
    img = Image.open(origen).convert("RGB")
    lado = min(img.size)
    recorte = round(lado * 0.06)  # quita parte del margen para que el dibujo llene más
    img = img.crop((recorte, recorte, lado - recorte, lado - recorte))
    img.resize((256, 256), Image.LANCZOS).save(DIR_IMG / "icono.png")
    img.save(DIR_IMG / "icono.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("  icono.png, icono.ico")


def extraer_fuentes():
    comprimido = RAIZ / "assets" / "founts" / "Orbitron.zip"
    if not comprimido.exists():
        return
    DIR_FUENTES.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(comprimido) as z:
        for interno in ("static/Orbitron-Bold.ttf", "static/Orbitron-Regular.ttf", "OFL.txt"):
            destino = DIR_FUENTES / Path(interno).name
            if not destino.exists():
                destino.write_bytes(z.read(interno))
                print(f"  fuentes/{destino.name}")


if __name__ == "__main__":
    DIR_IMG.mkdir(parents=True, exist_ok=True)
    for nombre, datos in HOJAS.items():
        procesar_hoja(nombre, datos)
    procesar_fondos()
    procesar_logo()
    procesar_icono()
    procesar_intro()
    extraer_fuentes()
    print("Listo.")

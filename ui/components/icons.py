"""
Fábrica de Iconos Vectoriales Monocromos y Puntos de Estado (ui/components/icons.py)
KestrelWOL - CustomTkinter (Offline-First, Zero Emojis)

Renderiza iconos vectoriales nítidos de contorno (trazo ~1.5px mediante supersampling 4x)
y micro-indicadores circulares de 6px usando Pillow + CTkImage.
"""

from functools import lru_cache
from typing import Tuple
import customtkinter as ctk
from PIL import Image, ImageDraw


def _new_canvas(size: int, scale: int = 4) -> Tuple[Image.Image, ImageDraw.ImageDraw, int]:
    px = size * scale
    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    return img, draw, scale


def _finalize(img: Image.Image, size: int) -> ctk.CTkImage:
    resized = img.resize((size, size), Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=resized, dark_image=resized, size=(size, size))


@lru_cache(maxsize=64)
def get_status_dot(color: str = "#10B981", size: int = 6) -> ctk.CTkImage:
    """Genera un punto de estado circular limpio de 6px (por defecto)."""
    img, draw, s = _new_canvas(size, scale=4)
    pad = 1
    end = size * s - 1 - pad
    draw.ellipse((pad, pad, end, end), fill=color)
    return _finalize(img, size)


@lru_cache(maxsize=256)
def get_icon(name: str, color: str = "#E2E8F0", size: int = 14) -> ctk.CTkImage:
    """
    Genera un icono vectorial de contorno monocromo (trazo 1.5px) en tamaño `size`.
    """
    img, draw, s = _new_canvas(size, scale=4)
    w = max(4, round(1.5 * s))
    u = size * s  # unidad total del lienzo supersampleado

    def pt(x_norm: float, y_norm: float) -> Tuple[float, float]:
        return (x_norm * u, y_norm * u)

    def box(x1: float, y1: float, x2: float, y2: float) -> Tuple[float, float, float, float]:
        return (x1 * u, y1 * u, x2 * u, y2 * u)

    if name == "power":
        draw.arc(box(0.18, 0.22, 0.82, 0.86), start=-55, end=235, fill=color, width=w)
        draw.line([pt(0.50, 0.12), pt(0.50, 0.50)], fill=color, width=w)

    elif name == "power_off":
        draw.ellipse(box(0.16, 0.16, 0.84, 0.84), outline=color, width=w)
        draw.rectangle(box(0.38, 0.38, 0.62, 0.62), outline=color, width=w)

    elif name == "refresh":
        draw.arc(box(0.18, 0.18, 0.82, 0.82), start=45, end=330, fill=color, width=w)
        draw.line([pt(0.76, 0.16), pt(0.76, 0.38), pt(0.56, 0.34)], fill=color, width=w)

    elif name == "monitor":
        draw.rounded_rectangle(box(0.12, 0.16, 0.88, 0.68), radius=1.2 * s, outline=color, width=w)
        draw.line([pt(0.50, 0.68), pt(0.50, 0.84)], fill=color, width=w)
        draw.line([pt(0.30, 0.84), pt(0.70, 0.84)], fill=color, width=w)

    elif name == "terminal":
        draw.rounded_rectangle(box(0.12, 0.18, 0.88, 0.82), radius=1.2 * s, outline=color, width=w)
        draw.line([pt(0.28, 0.38), pt(0.42, 0.50), pt(0.28, 0.62)], fill=color, width=w)
        draw.line([pt(0.50, 0.62), pt(0.70, 0.62)], fill=color, width=w)

    elif name == "clock":
        draw.ellipse(box(0.14, 0.14, 0.86, 0.86), outline=color, width=w)
        draw.line([pt(0.50, 0.28), pt(0.50, 0.52), pt(0.68, 0.62)], fill=color, width=w)

    elif name == "edit":
        draw.line([pt(0.20, 0.80), pt(0.26, 0.58), pt(0.66, 0.18), pt(0.82, 0.34), pt(0.42, 0.74), pt(0.20, 0.80)], fill=color, width=w)
        draw.line([pt(0.58, 0.26), pt(0.74, 0.42)], fill=color, width=w)

    elif name == "trash":
        draw.line([pt(0.18, 0.28), pt(0.82, 0.28)], fill=color, width=w)
        draw.line([pt(0.36, 0.28), pt(0.38, 0.16), pt(0.62, 0.16), pt(0.64, 0.28)], fill=color, width=w)
        draw.line([pt(0.26, 0.28), pt(0.30, 0.84), pt(0.70, 0.84), pt(0.74, 0.28)], fill=color, width=w)
        draw.line([pt(0.43, 0.42), pt(0.43, 0.70)], fill=color, width=w)
        draw.line([pt(0.57, 0.42), pt(0.57, 0.70)], fill=color, width=w)

    elif name == "close":
        draw.line([pt(0.24, 0.24), pt(0.76, 0.76)], fill=color, width=w)
        draw.line([pt(0.76, 0.24), pt(0.24, 0.76)], fill=color, width=w)

    elif name == "eye":
        draw.arc(box(0.10, 0.22, 0.90, 0.78), start=195, end=345, fill=color, width=w)
        draw.arc(box(0.10, 0.22, 0.90, 0.78), start=15, end=165, fill=color, width=w)
        draw.ellipse(box(0.38, 0.38, 0.62, 0.62), outline=color, width=w)

    elif name == "eye_off":
        draw.arc(box(0.10, 0.22, 0.90, 0.78), start=200, end=340, fill=color, width=w)
        draw.arc(box(0.10, 0.22, 0.90, 0.78), start=20, end=160, fill=color, width=w)
        draw.line([pt(0.20, 0.80), pt(0.80, 0.20)], fill=color, width=w)

    elif name == "upload":
        draw.line([pt(0.50, 0.64), pt(0.50, 0.18)], fill=color, width=w)
        draw.line([pt(0.32, 0.36), pt(0.50, 0.18), pt(0.68, 0.36)], fill=color, width=w)
        draw.line([pt(0.18, 0.64), pt(0.18, 0.82), pt(0.82, 0.82), pt(0.82, 0.64)], fill=color, width=w)

    elif name == "download":
        draw.line([pt(0.50, 0.16), pt(0.50, 0.62)], fill=color, width=w)
        draw.line([pt(0.32, 0.44), pt(0.50, 0.62), pt(0.68, 0.44)], fill=color, width=w)
        draw.line([pt(0.18, 0.64), pt(0.18, 0.82), pt(0.82, 0.82), pt(0.82, 0.64)], fill=color, width=w)

    elif name == "shield":
        draw.polygon(
            [pt(0.50, 0.14), pt(0.82, 0.26), pt(0.78, 0.58), pt(0.50, 0.86), pt(0.22, 0.58), pt(0.18, 0.26)],
            outline=color,
            width=w,
        )

    elif name == "file":
        draw.polygon(
            [pt(0.24, 0.14), pt(0.62, 0.14), pt(0.76, 0.28), pt(0.76, 0.86), pt(0.24, 0.86)],
            outline=color,
            width=w,
        )
        draw.line([pt(0.36, 0.44), pt(0.64, 0.44)], fill=color, width=w)
        draw.line([pt(0.36, 0.58), pt(0.64, 0.58)], fill=color, width=w)
        draw.line([pt(0.36, 0.72), pt(0.54, 0.72)], fill=color, width=w)

    elif name == "search":
        draw.ellipse(box(0.16, 0.16, 0.68, 0.68), outline=color, width=w)
        draw.line([pt(0.61, 0.61), pt(0.84, 0.84)], fill=color, width=w)

    elif name == "plus":
        draw.line([pt(0.50, 0.20), pt(0.50, 0.80)], fill=color, width=w)
        draw.line([pt(0.20, 0.50), pt(0.80, 0.50)], fill=color, width=w)

    elif name == "check":
        draw.line([pt(0.20, 0.52), pt(0.42, 0.74), pt(0.80, 0.28)], fill=color, width=w)

    elif name == "tag":
        draw.polygon(
            [pt(0.16, 0.16), pt(0.50, 0.16), pt(0.84, 0.50), pt(0.50, 0.84), pt(0.16, 0.50)],
            outline=color,
            width=w,
        )
        draw.ellipse(box(0.28, 0.28, 0.38, 0.38), fill=color)

    elif name == "alert":
        draw.polygon([pt(0.50, 0.16), pt(0.86, 0.82), pt(0.14, 0.82)], outline=color, width=w)
        draw.line([pt(0.50, 0.40), pt(0.50, 0.60)], fill=color, width=w)
        draw.ellipse(box(0.46, 0.68, 0.54, 0.76), fill=color)

    elif name == "sliders":
        draw.line([pt(0.16, 0.30), pt(0.84, 0.30)], fill=color, width=w)
        draw.line([pt(0.16, 0.70), pt(0.84, 0.70)], fill=color, width=w)
        draw.ellipse(box(0.28, 0.20, 0.44, 0.40), fill=color)
        draw.ellipse(box(0.56, 0.60, 0.72, 0.80), fill=color)

    return _finalize(img, size)

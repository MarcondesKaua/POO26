"""Ferramentas de pixel art: canvas, contorno, ampliação e salvamento de folhas de sprites."""
import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ESCALA = 2  # cada pixel "de arte" vira 2x2 pixels na tela
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")
MANIFESTO = {}  # nome -> [largura_quadro, altura_quadro, total_quadros, colunas]


def hexa(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


class Pix:
    """Pequeno canvas RGBA para desenhar pixel art na resolução nativa."""

    def __init__(self, w, h, fundo=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w, h), fundo)
        self.d = ImageDraw.Draw(self.img)

    def _camada(self, fn, c):
        """Desenha formas semitransparentes MISTURANDO com o que já existe."""
        if len(c) == 4 and c[3] < 255:
            tmp = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
            fn(ImageDraw.Draw(tmp))
            self.img.alpha_composite(tmp)
        else:
            fn(self.d)

    def r(self, x0, y0, x1, y1, c):
        if x1 >= x0 and y1 >= y0:
            self._camada(lambda d: d.rectangle([x0, y0, x1, y1], fill=c), c)

    def p(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            if len(c) == 4 and 0 < c[3] < 255:
                self.img.alpha_composite(Image.new("RGBA", (1, 1), c), (int(x), int(y)))
            else:
                self.img.putpixel((int(x), int(y)), c)

    def l(self, x0, y0, x1, y1, c, w=1):
        self._camada(lambda d: d.line([x0, y0, x1, y1], fill=c, width=w), c)

    def e(self, x0, y0, x1, y1, c):
        self._camada(lambda d: d.ellipse([x0, y0, x1, y1], fill=c), c)

    def poly(self, pts, c):
        self._camada(lambda d: d.polygon(pts, fill=c), c)

    def colar(self, outro, x=0, y=0):
        src = outro.img if isinstance(outro, Pix) else outro
        self.img.paste(src, (x, y), src)


def contorno(img, cor=(16, 10, 24, 255)):
    a = np.array(img)
    m = a[..., 3] > 0
    d = np.zeros_like(m)
    d[1:, :] |= m[:-1, :]
    d[:-1, :] |= m[1:, :]
    d[:, 1:] |= m[:, :-1]
    d[:, :-1] |= m[:, 1:]
    borda = d & ~m
    a[borda] = cor
    return Image.fromarray(a, "RGBA")


def ampliar(img, esc=ESCALA):
    return img.resize((img.width * esc, img.height * esc), Image.NEAREST)


def caminho(sub, nome):
    pasta = os.path.join(ASSETS, sub)
    os.makedirs(pasta, exist_ok=True)
    return os.path.join(pasta, nome)


def salvar(img, sub, nome, esc=ESCALA):
    img = img.img if isinstance(img, Pix) else img
    ampliar(img, esc).save(caminho(sub, nome))


def folha(frames):
    frames = [f.img if isinstance(f, Pix) else f for f in frames]
    w, h = frames[0].size
    sheet = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    return sheet


def salvar_folha(nome, frames, sub="sprites", esc=ESCALA, contornar=True):
    """Salva nome.png (virado p/ direita) e nome_l.png (espelhado, p/ esquerda)."""
    frames = [f.img if isinstance(f, Pix) else f for f in frames]
    if contornar:
        frames = [contorno(f) for f in frames]
    w, h = frames[0].size
    ampliar(folha(frames), esc).save(caminho(sub, nome + ".png"))
    espelhados = [ImageOps.mirror(f) for f in frames]
    ampliar(folha(espelhados), esc).save(caminho(sub, nome + "_l.png"))
    MANIFESTO[sub + "/" + nome] = [w * esc, h * esc, len(frames), len(frames)]


def salvar_manifesto():
    with open(os.path.join(ASSETS, "manifesto.json"), "w", encoding="utf-8") as f:
        json.dump(MANIFESTO, f, indent=1)

"""Fundos com parallax, tela de título, logo e vinheta."""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .pix import Pix, hexa, salvar, caminho, ESCALA

LARG, ALT = 512, 288  # nativo; x2 = 1024x576


def gradiente(topo, base, w=LARG, h=ALT):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(topo, dtype=float)[None, None, :]
    b = np.array(base, dtype=float)[None, None, :]
    arr = (a + (b - a) * t).repeat(w, axis=1).astype(np.uint8)
    img = Image.fromarray(arr, "RGB").convert("RGBA")
    p = Pix(w, h)
    p.img = img
    p.d = ImageDraw.Draw(img)
    return p


def estrelas(p, rng, n=140, ymax=170):
    for _ in range(n):
        x, y = rng.randint(0, p.w - 1), rng.randint(0, ymax)
        b = rng.randint(150, 255)
        p.p(x, y, (b, b, min(255, b + 20), 255))
    for _ in range(10):
        x, y = rng.randint(4, p.w - 5), rng.randint(0, ymax)
        c = (255, 255, 255, 255)
        p.p(x, y, c)
        p.p(x - 1, y, (255, 255, 255, 140))
        p.p(x + 1, y, (255, 255, 255, 140))
        p.p(x, y - 1, (255, 255, 255, 140))
        p.p(x, y + 1, (255, 255, 255, 140))


def lua(p, cx, cy, r, cor, cor_c, halo=True):
    if halo:
        for k in range(8, 0, -1):
            a = 10 + (8 - k) * 3
            p.e(cx - r - k * 3, cy - r - k * 3, cx + r + k * 3, cy + r + k * 3, (cor[0], cor[1], cor[2], a))
    p.e(cx - r, cy - r, cx + r, cy + r, cor)
    for dx, dy, rr in ((-r // 3, -r // 4, r // 5), (r // 4, r // 5, r // 4), (-r // 5, r // 2, r // 7)):
        p.e(cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr, cor_c)


def nuvens(p, rng, cor, y0, y1, n=7):
    for _ in range(n):
        x = rng.randint(0, p.w)
        y = rng.randint(y0, y1)
        for k in range(rng.randint(3, 6)):
            w = rng.randint(30, 70)
            h = rng.randint(6, 12)
            for off in (0, -p.w, p.w):
                p.e(x + k * 22 - w // 2 + off, y - h // 2 + rng.randint(-2, 2), x + k * 22 + w // 2 + off, y + h // 2, cor)


def castelo(p, x, base, esc, cor, luz):
    def torre(x0, w, h, tel):
        p.r(x0, base - h, x0 + w, base, cor)
        if tel:
            p.poly([(x0 - 2, base - h), (x0 + w / 2, base - h - tel), (x0 + w + 2, base - h)], cor)
        else:
            for i in range(x0, x0 + w, 4):
                p.r(i, base - h - 3, i + 1, base - h, cor)
        if luz:
            for j in range(base - h + 8, base - 8, 14):
                p.r(x0 + w // 2 - 1, j, x0 + w // 2 + 1, j + 3, luz)

    e = esc
    torre(x, int(26 * e), int(90 * e), int(34 * e))
    torre(x + int(30 * e), int(34 * e), int(60 * e), 0)
    torre(x + int(68 * e), int(22 * e), int(120 * e), int(40 * e))
    torre(x + int(94 * e), int(34 * e), int(70 * e), 0)
    torre(x + int(132 * e), int(24 * e), int(100 * e), int(30 * e))
    p.r(x, base - 18, x + int(160 * e), base, cor)
    if luz:
        for i in range(x + 10, x + int(150 * e), 22):
            p.r(i, base - 40, i + 3, base - 33, luz)


def morro(p, rng, base, amp, cor, passo=16, fase=0):
    pts = [(-4, p.h + 2)]
    for x in range(-4, p.w + passo, passo):
        # periódico em p.w para o fundo emendar
        y = base - amp * (0.5 + 0.5 * math.sin((x / p.w) * 2 * math.pi * 3 + fase)) - rng_det(x, 5) % (amp // 3 + 1)
        pts.append((x, y))
    pts.append((p.w + passo, p.h + 2))
    p.poly(pts, cor)


def rng_det(x, k):
    return int((math.sin(x * 12.9898 + k * 78.233) * 43758.5453) % 1 * 100)


def arvore_morta(p, x, base, altura, cor, rng):
    p.poly([(x - 3, base), (x + 3, base), (x + 1, base - altura), (x - 1, base - altura)], cor)
    def ramo(x0, y0, ang, comp, prof):
        if prof == 0 or comp < 4:
            return
        x1 = x0 + math.cos(ang) * comp
        y1 = y0 - math.sin(ang) * comp
        p.l(x0, y0, x1, y1, cor, max(1, prof - 1))
        ramo(x1, y1, ang + rng.uniform(0.3, 0.8), comp * 0.7, prof - 1)
        ramo(x1, y1, ang - rng.uniform(0.3, 0.8), comp * 0.7, prof - 1)
    ramo(x, base - altura * 0.55, math.pi / 2 + 0.7, altura * 0.45, 4)
    ramo(x, base - altura * 0.7, math.pi / 2 - 0.7, altura * 0.4, 4)
    ramo(x, base - altura, math.pi / 2, altura * 0.3, 3)


def neblina(p, y0, cor, alt=40):
    for i in range(alt):
        a = int(cor[3] * (1 - abs(i - alt / 2) / (alt / 2)) ** 1.5)
        p.r(0, y0 + i, p.w, y0 + i, (cor[0], cor[1], cor[2], a))


def vazio():
    return Pix(LARG, ALT)


# ---------------------------------------------------------------- temas


def tema_cemiterio():
    rng = random.Random(21)
    f = gradiente((10, 6, 32), (86, 46, 92))
    estrelas(f, rng)
    lua(f, 380, 80, 34, hexa("#f4eed8"), hexa("#d2c9b0"))
    nuvens(f, rng, (40, 24, 66, 150), 60, 140)
    morro(f, rng, 250, 60, hexa("#1c1034"), 20, 1.0)
    m = vazio()
    castelo(m, 60, 236, 1.5, hexa("#150c28"), hexa("#ffcf70"))
    morro(m, rng, 270, 40, hexa("#120a24"), 16, 2.0)
    neblina(m, 200, (150, 120, 190, 70), 60)
    n = vazio()
    for x in (40, 170, 300, 440):
        arvore_morta(n, x, 290, rng.randint(90, 130), hexa("#0a0614"), rng)
    morro(n, rng, 292, 14, hexa("#0a0614"), 12, 0.5)
    neblina(n, 235, (110, 90, 150, 60), 50)
    return f, m, n


def tema_salao():
    rng = random.Random(33)
    f = gradiente((24, 10, 34), (70, 24, 46))
    for y in range(0, ALT, 16):
        f.r(0, y, LARG, y, (16, 6, 24, 120))
        for x in range((y // 16 % 2) * 16, LARG, 32):
            f.r(x, y, x, y + 15, (16, 6, 24, 120))
    for x in range(40, LARG, 128):
        f.e(x - 22, 40, x + 22, 100, hexa("#4a6aa8"))
        f.r(x - 22, 70, x + 22, 150, hexa("#4a6aa8"))
        f.e(x - 14, 50, x + 14, 90, hexa("#9ac0f0"))
        f.r(x - 14, 70, x + 14, 140, hexa("#9ac0f0"))
        f.r(x - 1, 48, x, 150, hexa("#2a2040"))
        f.r(x - 22, 100, x + 22, 101, hexa("#2a2040"))
    m = vazio()
    for x in range(0, LARG, 128):
        m.r(x + 8, 40, x + 24, ALT, hexa("#1a0e26"))
        m.r(x + 104, 40, x + 120, ALT, hexa("#1a0e26"))
        m.e(x + 8, 10, x + 120, 100, hexa("#1a0e26"))
        m.e(x + 24, 26, x + 104, 100, (0, 0, 0, 0))
        m.r(x + 24, 63, x + 104, 100, (0, 0, 0, 0))
    n = vazio()
    for x in range(30, LARG, 170):
        n.r(x, 0, x + 3, 120 + rng.randint(0, 40), hexa("#0e0716"))
        n.poly([(x - 14, 0), (x + 17, 0), (x + 10, 70), (x - 6, 90)], (96, 18, 40, 220))
    neblina(n, 230, (90, 50, 110, 70), 60)
    return f, m, n


def tema_torre():
    rng = random.Random(44)
    f = gradiente((8, 18, 30), (36, 66, 86))
    nuvens(f, rng, (14, 30, 44, 200), 10, 120, 10)
    # relâmpago
    x, y = 150, 0
    for _ in range(9):
        nx, ny = x + rng.randint(-14, 14), y + rng.randint(14, 26)
        f.l(x, y, nx, ny, (230, 240, 255, 255), 1)
        x, y = nx, ny
    m = vazio()
    for cx, cy, r in ((120, 150, 78), (400, 110, 56), (270, 220, 40)):
        for k in range(14):
            ang = k * math.pi * 2 / 14
            m.poly([(cx + math.cos(ang - .1) * r, cy + math.sin(ang - .1) * r), (cx + math.cos(ang + .1) * r, cy + math.sin(ang + .1) * r),
                    (cx + math.cos(ang + .08) * (r + 10), cy + math.sin(ang + .08) * (r + 10)), (cx + math.cos(ang - .08) * (r + 10), cy + math.sin(ang - .08) * (r + 10))], hexa("#0f1a28"))
        m.e(cx - r, cy - r, cx + r, cy + r, hexa("#0f1a28"))
        m.e(cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12, (0, 0, 0, 0))
        m.e(cx - 8, cy - 8, cx + 8, cy + 8, hexa("#0f1a28"))
        m.l(cx, cy, cx + r - 14, cy, hexa("#0f1a28"), 3)
        m.l(cx, cy, cx, cy - r + 14, hexa("#0f1a28"), 3)
    n = vazio()
    for x in range(20, LARG, 140):
        h = rng.randint(130, 210)
        n.r(x, ALT - h, x + 22, ALT, hexa("#080e18"))
        n.poly([(x - 4, ALT - h), (x + 26, ALT - h), (x + 18, ALT - h - 10), (x + 4, ALT - h - 4)], hexa("#080e18"))
    neblina(n, 220, (80, 120, 150, 70), 60)
    return f, m, n


def tema_arena():
    rng = random.Random(55)
    f = gradiente((24, 4, 12), (90, 14, 28))
    estrelas(f, rng, 60, 120)
    lua(f, 256, 120, 90, hexa("#c82020"), hexa("#8a1414"))
    nuvens(f, rng, (40, 6, 20, 170), 90, 200, 6)
    m = vazio()
    for x in range(0, LARG, 64):
        m.r(x + 24, 60, x + 40, ALT, hexa("#14040c"))
        m.poly([(x + 16, 60), (x + 48, 60), (x + 32, 20)], hexa("#14040c"))
    n = vazio()
    for x in range(0, LARG, 256):
        n.poly([(x + 20, ALT), (x + 36, 120), (x + 52, ALT)], hexa("#0a0208"))
        n.poly([(x + 200, ALT), (x + 216, 90), (x + 232, ALT)], hexa("#0a0208"))
    neblina(n, 220, (150, 30, 50, 70), 60)
    return f, m, n


def gerar_fundos():
    for nome, fn in (("cem", tema_cemiterio), ("salao", tema_salao), ("torre", tema_torre), ("arena", tema_arena)):
        for i, camada in enumerate(fn()):
            salvar(camada, "bg", f"{nome}_{i}.png")


# ---------------------------------------------------------------- título, logo, vinheta


def gerar_titulo():
    rng = random.Random(77)
    f = gradiente((6, 4, 22), (110, 40, 70))
    estrelas(f, rng, 200, 190)
    lua(f, 330, 110, 60, hexa("#f6efd8"), hexa("#d6ccb0"))
    nuvens(f, rng, (50, 24, 70, 170), 70, 190, 8)
    morro(f, rng, 270, 50, hexa("#180a2a"), 16, 0.7)
    castelo(f, 120, 252, 1.5, hexa("#0e0618"), hexa("#ffcf70"))
    morro(f, rng, 292, 22, hexa("#08040f"), 12, 2.5)
    neblina(f, 220, (180, 130, 190, 80), 60)
    for x in (30, 440):
        arvore_morta(f, x, 288, 170, hexa("#06030c"), rng)
    # cerca de ferro
    for x in range(0, LARG, 9):
        f.r(x, 262, x + 1, 288, hexa("#06030c"))
        f.poly([(x - 1, 262), (x + 1, 256), (x + 3, 262)], hexa("#06030c"))
    f.r(0, 272, LARG, 273, hexa("#06030c"))
    # morcegos
    for bx, by in ((90, 60), (110, 80), (420, 50), (60, 120), (470, 100), (240, 40)):
        f.poly([(bx, by), (bx - 8, by - 5), (bx - 4, by + 1), (bx, by + 3), (bx + 4, by + 1), (bx + 8, by - 5)], hexa("#06030c"))
    salvar(f, "bg", "titulo.png")


def _fonte(tam):
    for c in ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/timesbd.ttf"):
        if os.path.exists(c):
            return ImageFont.truetype(c, tam)
    return ImageFont.load_default(size=tam)


def gerar_logo():
    W, H = 900, 300
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    linhas = [("CASTELO", 120, 10), ("MALDITO", 120, 150)]
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for txt, tam, y in linhas:
        fonte = _fonte(tam)
        d = ImageDraw.Draw(base)
        bb = d.textbbox((0, 0), txt, font=fonte)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        ds = ImageDraw.Draw(sombra)
        ds.text((x + 4, y + 6), txt, font=fonte, fill=(0, 0, 0, 255), stroke_width=6, stroke_fill=(0, 0, 0, 255))
        mascara = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mascara).text((x, y), txt, font=fonte, fill=255)
        grad = Image.new("RGBA", (W, H))
        gd = ImageDraw.Draw(grad)
        for yy in range(H):
            t = ((yy - y) / max(1, tam * 1.1))
            t = max(0, min(1, t))
            cor = (int(255 - 70 * t), int(200 - 170 * t), int(80 - 60 * t), 255)
            gd.line([(0, yy), (W, yy)], fill=cor)
        contorno = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(contorno).text((x, y), txt, font=fonte, fill=(60, 4, 10, 255), stroke_width=5, stroke_fill=(60, 4, 10, 255))
        base.alpha_composite(contorno)
        base.paste(grad, (0, 0), mascara)
    sombra = sombra.filter(ImageFilter.GaussianBlur(3))
    final = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    final.alpha_composite(sombra)
    final.alpha_composite(base)
    final.save(caminho("ui", "logo.png"))


def gerar_vinheta(w=1024, h=576):
    y, x = np.mgrid[0:h, 0:w]
    dx = (x - w / 2) / (w / 2)
    dy = (y - h / 2) / (h / 2)
    r = np.sqrt(dx * dx * 0.8 + dy * dy)
    a = np.clip((r - 0.55) / 0.9, 0, 1) ** 1.6 * 190
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[..., 0] = 6
    arr[..., 1] = 2
    arr[..., 2] = 14
    arr[..., 3] = a.astype(np.uint8)
    Image.fromarray(arr, "RGBA").save(caminho("ui", "vinheta.png"))


def gerar_tudo():
    gerar_fundos()
    gerar_titulo()
    gerar_logo()
    gerar_vinheta()

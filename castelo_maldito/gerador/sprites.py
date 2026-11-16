"""Desenha (em código!) todos os sprites do jogo: herói, inimigos, chefe, projéteis, itens e tiles."""
import math
import random

from PIL import Image

from .pix import Pix, hexa, salvar, salvar_folha, MANIFESTO

# --------------------------------------------------------------------------- utilidades


def bmp(p, linhas, paleta, ox=0, oy=0, esc=1):
    """Desenha um bitmap descrito por caracteres."""
    for j, linha in enumerate(linhas):
        for i, ch in enumerate(linha):
            if ch in paleta:
                p.r(ox + i * esc, oy + j * esc, ox + i * esc + esc - 1, oy + j * esc + esc - 1, paleta[ch])


def girar(frame, ang):
    img = frame.img if isinstance(frame, Pix) else frame
    return img.rotate(ang, resample=Image.NEAREST, expand=False)


# --------------------------------------------------------------------------- HERÓI (20x36)

CASACO = hexa("#9b2335")
CASACO_E = hexa("#5e1220")
PELE = hexa("#f2cfa6")
CABELO = hexa("#e9e9f6")
CALCA = hexa("#323a5e")
BOTA = hexa("#2a2233")
CACHECOL = hexa("#e04848")
ACO = hexa("#e6eefa")
ACO_E = hexa("#8fa2c4")
OURO = hexa("#f0c040")

BRACOS = {  # ombro fixo (11,15); posição da mão e ponta da lâmina
    "baixo": ((14, 22), (17, 31)),
    "alto": ((8, 9), (2, 1)),
    "frente": ((16, 17), (19, 17)),
    "recuperar": ((15, 21), (18, 29)),
    "cima": ((14, 12), (17, 3)),
    "estocada": ((17, 16), None),
}


def heroi(pose):
    p = Pix(20, 36)
    by = pose.get("bob", 0)
    dx = pose.get("dx", 0)
    comp = pose.get("cachecol", 4)
    cdy = pose.get("cdy", 0)
    morto = pose.get("morto", False)
    # cachecol (atrás)
    p.r(7 + dx - comp, 13 + by + cdy, 8 + dx, 14 + by + cdy, CACHECOL)
    p.r(7 + dx - comp - 1, 14 + by + cdy + 1, 7 + dx - comp + 1, 15 + by + cdy + 1, CACHECOL)
    # pernas
    if not morto:
        for (x0, x1, y0, y1), tom in ((pose["A"], 0.8), (pose["B"], 1.0)):
            cor = CALCA if tom == 1.0 else hexa("#262c4a")
            p.r(x0 + dx, y0, x1 + dx, y1 - 2, cor)
            p.r(x0 + dx, y1 - 2, x1 + dx + 1, y1, BOTA)
    # tronco / casaco
    p.r(6 + dx, 13 + by, 14 + dx, 22 + by, CASACO)
    p.r(5 + dx, 22 + by, 15 + dx, 27 + by, CASACO)
    p.r(5 + dx, 14 + by, 7 + dx, 27 + by, CASACO_E)
    p.r(7 + dx, 21 + by, 13 + dx, 21 + by, hexa("#2a1018"))
    p.p(10 + dx, 21 + by, OURO)
    p.r(5 + dx, 27 + by, 15 + dx, 27 + by, CASACO_E)
    # gola
    p.r(7 + dx, 12 + by, 13 + dx, 13 + by, CASACO_E)
    # cabeça
    p.r(8 + dx, 5 + by, 13 + dx, 11 + by, PELE)
    p.r(7 + dx, 3 + by, 14 + dx, 6 + by, CABELO)
    p.r(6 + dx, 5 + by, 8 + dx, 12 + by, CABELO)
    p.p(14 + dx, 8 + by, PELE)
    if pose.get("ferido"):
        p.l(11 + dx, 8 + by, 13 + dx, 8 + by, hexa("#402020"))
    else:
        p.p(12 + dx, 8 + by, hexa("#d02828"))
        p.p(11 + dx, 8 + by, hexa("#ffffff"))
    p.p(12 + dx, 11 + by, hexa("#c08060"))
    # braço + espada
    mao, ponta = BRACOS[pose.get("braco", "baixo")]
    ombro = (11 + dx, 15 + by)
    mao = (mao[0] + dx, mao[1] + by)
    p.l(ombro[0], ombro[1], mao[0], mao[1], CASACO, 2)
    p.p(mao[0], mao[1], PELE)
    if ponta is not None:
        ponta = (ponta[0] + dx, ponta[1] + by)
        p.l(mao[0], mao[1], ponta[0], ponta[1], ACO_E, 2)
        p.l(mao[0], mao[1], ponta[0], ponta[1], ACO, 1)
        # guarda dourada
        gx, gy = mao
        p.r(gx - 1, gy, gx + 1, gy, OURO)
    if morto:
        p.r(16, 22, 17, 34, ACO)  # espada fincada no chão
        p.r(15, 22, 18, 22, OURO)
    return p


def heroi_frames():
    P = {
        "idle": dict(A=(8, 10, 25, 34), B=(11, 13, 25, 34)),
        "w0": dict(A=(6, 8, 25, 34), B=(12, 14, 25, 34), bob=1),
        "w1": dict(A=(9, 11, 25, 32), B=(10, 12, 25, 34)),
        "w2": dict(A=(12, 14, 25, 34), B=(6, 8, 25, 34), bob=1),
        "w3": dict(A=(10, 12, 25, 34), B=(9, 11, 25, 32)),
        "pulo": dict(A=(11, 13, 25, 30), B=(8, 10, 25, 32), braco="cima", cachecol=6, cdy=2),
        "queda": dict(A=(7, 9, 25, 34), B=(12, 14, 25, 34), braco="cima", cachecol=5, cdy=-2),
        "prep": dict(A=(5, 7, 25, 34), B=(12, 14, 25, 34), braco="alto", dx=-1),
        "golpe": dict(A=(6, 8, 25, 34), B=(13, 15, 25, 34), braco="frente", dx=1, bob=1),
        "recup": dict(A=(6, 8, 25, 34), B=(12, 14, 25, 34), braco="recuperar"),
        "dash": dict(A=(4, 7, 27, 32), B=(6, 9, 28, 33), dx=2, bob=3, cachecol=8),
        "ferido": dict(A=(7, 9, 25, 34), B=(11, 13, 25, 34), braco="alto", dx=-1, ferido=True),
        "morto": dict(A=(8, 10, 25, 34), B=(11, 13, 25, 34), bob=12, morto=True, ferido=True, braco="baixo"),
        "cast": dict(A=(6, 8, 25, 34), B=(12, 14, 25, 34), braco="estocada"),
    }
    ordem = ["idle", "w0", "w1", "w2", "w3", "pulo", "queda", "prep", "golpe", "recup", "dash", "ferido", "morto", "cast"]
    return [heroi(P[k]) for k in ordem]


# --------------------------------------------------------------------------- INIMIGOS


def zumbi(f):
    p = Pix(18, 32)
    pele = hexa("#86ad6a")
    pele_e = hexa("#58784a")
    roupa = hexa("#6b4a34")
    roupa_e = hexa("#45301f")
    off = [(-2, 2), (0, 0), (2, -2), (0, 0)][f]
    lift = [(0, 0), (1, 0), (0, 0), (0, 1)][f]
    bob = 1 if f in (0, 2) else 0
    # pernas
    p.r(6 + off[0], 22, 8 + off[0], 30 - lift[0], roupa_e)
    p.r(6 + off[0], 29 - lift[0], 9 + off[0], 30 - lift[0], pele_e)
    p.r(9 + off[1], 22, 11 + off[1], 30 - lift[1], roupa)
    p.r(9 + off[1], 29 - lift[1], 12 + off[1], 30 - lift[1], pele)
    # tronco rasgado
    p.r(5, 12 + bob, 12, 23 + bob, roupa)
    p.r(5, 12 + bob, 6, 23 + bob, roupa_e)
    p.p(8, 20 + bob, pele_e)
    p.p(9, 21 + bob, pele_e)
    p.r(5, 23 + bob, 6, 25 + bob, roupa_e)
    p.r(9, 23 + bob, 10, 26 + bob, roupa)
    # cabeça inclinada
    p.r(7, 4 + bob, 13, 11 + bob, pele)
    p.r(7, 3 + bob, 12, 4 + bob, hexa("#2c3a2a"))
    p.p(11, 7 + bob, hexa("#ff3030"))
    p.p(12, 7 + bob, hexa("#ff3030"))
    p.r(10, 10 + bob, 13, 10 + bob, hexa("#3a1a1a"))
    # braços esticados
    for ay in (14, 16):
        p.r(11, ay + bob, 17, ay + 1 + bob, pele if ay == 14 else pele_e)
    p.p(17, 14 + bob, hexa("#cfe0b0"))
    return p


def morcego(f):
    p = Pix(20, 14)
    corpo = hexa("#4a2a63")
    asa = hexa("#33204a")
    asa_c = hexa("#6a3a8a")
    if f == 3:  # dormindo, de cabeça pra baixo
        p.e(6, 1, 13, 11, asa)
        p.e(8, 1, 11, 5, corpo)
        p.p(8, 3, hexa("#ff4040"))
        p.p(11, 3, hexa("#ff4040"))
        p.p(9, 5, hexa("#ffffff"))
        p.p(10, 5, hexa("#ffffff"))
        return p
    p.e(8, 5, 12, 11, corpo)
    p.p(9, 4, corpo)
    p.p(11, 4, corpo)
    p.p(9, 7, hexa("#ff4040"))
    p.p(11, 7, hexa("#ff4040"))
    p.p(9, 10, hexa("#ffffff"))
    p.p(11, 10, hexa("#ffffff"))
    if f == 0:
        pts_l = [(8, 7), (1, 0), (3, 5), (5, 4), (6, 8)]
    elif f == 1:
        pts_l = [(8, 7), (0, 5), (3, 9), (5, 8), (6, 9)]
    else:
        pts_l = [(8, 8), (2, 13), (4, 10), (6, 11), (7, 10)]
    pts_r = [(19 - x, y) for x, y in pts_l]
    p.poly(pts_l, asa)
    p.poly(pts_r, asa)
    p.l(pts_l[0][0], pts_l[0][1], pts_l[1][0], pts_l[1][1], asa_c)
    p.l(pts_r[0][0], pts_r[0][1], pts_r[1][0], pts_r[1][1], asa_c)
    return p


def esqueleto(f):
    p = Pix(18, 34)
    osso = hexa("#ece6d2")
    osso_e = hexa("#a79f88")
    esc = hexa("#2a2230")
    off = [(-2, 2), (0, 0), (2, -2), (0, 0)][f if f < 4 else 1]
    lift = [(0, 0), (1, 0), (0, 0), (0, 1)][f if f < 4 else 1]
    # pernas
    for (o, l, cor) in ((off[0], lift[0], osso_e), (off[1], lift[1], osso)):
        p.r(7 + o, 23, 8 + o, 31 - l, cor)
        p.r(6 + o, 31 - l, 9 + o, 32 - l, cor)
    # pélvis
    p.r(6, 21, 11, 23, osso)
    # costelas
    for y in range(12, 21):
        cor = osso if (y % 2 == 0) else esc
        p.r(6, y, 11, y, cor)
    p.r(8, 11, 9, 22, osso_e)
    # braço (esquerdo atrás / direito à frente)
    if f == 4:  # arremesso: braço levantado segurando osso
        p.r(11, 8, 12, 14, osso)
        p.r(10, 3, 15, 4, osso)
        p.p(10, 2, osso)
        p.p(10, 5, osso)
        p.p(15, 2, osso)
        p.p(15, 5, osso)
    else:
        p.r(11, 13, 12, 20, osso)
        p.r(5, 13, 5, 19, osso_e)
    # crânio
    p.r(6, 3, 12, 9, osso)
    p.r(7, 10, 11, 11, osso_e)
    p.r(7, 5, 8, 7, esc)
    p.r(10, 5, 11, 7, esc)
    p.p(8, 6, hexa("#ff3030"))
    p.p(11, 6, hexa("#ff3030"))
    p.p(9, 8, esc)
    return p


def cavaleiro(f):
    p = Pix(26, 40)
    aco = hexa("#a9b8cf")
    aco_c = hexa("#d6e2f2")
    aco_e = hexa("#5f6f8c")
    plumas = hexa("#c0283c")
    ouro = hexa("#e0b040")
    azul = hexa("#2a4a9a")
    w = f if f < 4 else 1
    off = [(-2, 2), (0, 0), (2, -2), (0, 0)][w]
    lift = [(0, 0), (1, 0), (0, 0), (0, 1)][w]
    bob = 1 if w in (0, 2) else 0
    # pernas
    for (o, l, cor) in ((off[0], lift[0], aco_e), (off[1], lift[1], aco)):
        p.r(8 + o, 27, 11 + o, 37 - l, cor)
        p.r(8 + o, 36 - l, 13 + o, 37 - l, aco_e)
    # corpo
    p.r(6, 14 + bob, 15, 28 + bob, aco)
    p.r(6, 14 + bob, 8, 28 + bob, aco_e)
    p.r(9, 16 + bob, 12, 17 + bob, aco_c)
    p.r(6, 25 + bob, 15, 26 + bob, hexa("#403020"))
    p.r(5, 12 + bob, 16, 15 + bob, aco_c)  # ombreira
    # elmo
    p.r(8, 3 + bob, 14, 12 + bob, aco)
    p.r(8, 3 + bob, 9, 12 + bob, aco_e)
    p.r(10, 7 + bob, 14, 7 + bob, hexa("#10101a"))  # viseira
    p.p(13, 7 + bob, hexa("#ff4040"))
    p.r(10, 0 + bob, 12, 3 + bob, plumas)
    p.r(8, 1 + bob, 9, 3 + bob, plumas)
    # espada
    if f == 4:  # levantada
        p.l(9, 14, 5, 2, aco_c, 2)
        p.r(4, 13, 11, 14, ouro)
    elif f == 5:  # golpe
        p.l(13, 20, 25, 30, aco_c, 2)
        p.r(12, 19, 14, 21, ouro)
    else:
        p.l(10, 22, 8, 36, aco_c, 1)
        p.r(8, 21, 12, 22, ouro)
    # escudo (frente = direita)
    p.poly([(15, 14 + bob), (23, 14 + bob), (23, 25 + bob), (19, 33 + bob), (15, 25 + bob)], azul)
    p.l(19, 15 + bob, 19, 31 + bob, ouro)
    p.l(16, 20 + bob, 22, 20 + bob, ouro)
    p.l(15, 14 + bob, 23, 14 + bob, ouro)
    return p


def medusa(f):
    p = Pix(18, 18)
    pedra = hexa("#a9c4a0")
    pedra_e = hexa("#6c8a68")
    cobra = hexa("#3d8a4a")
    p.e(4, 5, 13, 15, pedra)
    p.e(4, 5, 7, 15, pedra_e)
    # cobras no cabelo
    pts = [(3, 7), (2, 4), (4, 2), (7, 3), (10, 2), (13, 3), (15, 5), (14, 8)]
    if f == 1:
        pts = [(3, 8), (1, 6), (3, 3), (6, 1), (10, 3), (13, 1), (16, 4), (14, 7)]
    for a, b in zip(pts, pts[1:]):
        p.l(a[0], a[1], b[0], b[1], cobra, 2)
    p.p(2, 4, hexa("#ff4040"))
    p.p(15, 5, hexa("#ff4040"))
    p.r(7, 8, 8, 9, hexa("#ff2020"))
    p.r(11, 8, 12, 9, hexa("#ff2020"))
    p.r(8, 12, 11, 12, hexa("#402020"))
    return p


def fantasma(f):
    p = Pix(20, 30)
    cor = hexa("#d9e6ff")
    cor_e = hexa("#8fa6d8")
    p.e(3, 2, 16, 16, cor)
    p.r(3, 9, 16, 24, cor)
    # barra ondulada
    for i, x in enumerate(range(3, 17, 3)):
        h = 3 if (i + f) % 2 == 0 else 0
        p.r(x, 24, x + 2, 26 + h, cor)
    p.r(3, 9, 5, 24, cor_e)
    p.e(6, 8, 9, 13, hexa("#1a1830"))
    p.e(11, 8, 14, 13, hexa("#1a1830"))
    p.p(8, 10, hexa("#ffffff"))
    p.p(13, 10, hexa("#ffffff"))
    p.e(8, 15, 11, 19, hexa("#1a1830"))
    return p


# --------------------------------------------------------------------------- CHEFE: Conde Vorthal (64x72)


def chefe(pose):
    p = Pix(64, 72)
    capa = hexa("#1c1233")
    capa_i = hexa("#8a1428")
    capa_c = hexa("#2e1f52")
    pele = hexa("#ece4f4")
    cabelo = hexa("#0e0c18")
    olho = hexa("#ff3030")
    abrir = pose in ("cast", "rugido")
    # capa
    if pose == "idle1":
        pts = [(22, 24), (42, 24), (60, 66), (52, 70), (44, 66), (36, 71), (28, 66), (20, 70), (12, 66), (4, 66)]
    elif abrir:
        pts = [(22, 24), (42, 24), (63, 50), (58, 60), (46, 56), (32, 66), (18, 56), (6, 60), (1, 50)]
    elif pose == "golpe":
        pts = [(22, 24), (42, 24), (50, 50), (60, 62), (40, 64), (26, 70), (14, 60), (8, 58)]
    else:
        pts = [(22, 24), (42, 24), (54, 64), (46, 69), (38, 65), (32, 70), (26, 65), (18, 69), (10, 64)]
    p.poly(pts, capa)
    # forro vermelho
    inner = [(26, 28), (38, 28), (44, 60), (32, 66), (20, 60)]
    if abrir:
        inner = [(25, 28), (39, 28), (56, 52), (32, 62), (8, 52)]
    p.poly(inner, capa_i)
    p.l(22, 24, 4, 64, capa_c)
    # corpo
    p.r(26, 22, 38, 52, capa)
    p.r(28, 24, 36, 40, hexa("#3a1840"))
    p.r(31, 26, 33, 30, hexa("#d01838"))  # joia
    p.r(29, 38, 35, 39, hexa("#c09a30"))
    # golas
    p.poly([(22, 26), (23, 8), (29, 22)], capa)
    p.poly([(42, 26), (41, 8), (35, 22)], capa)
    p.poly([(25, 25), (25, 12), (28, 22)], capa_i)
    p.poly([(39, 25), (39, 12), (36, 22)], capa_i)
    # cabeça
    p.r(27, 8, 37, 21, pele)
    p.r(26, 6, 38, 11, cabelo)
    p.poly([(27, 11), (31, 15), (27, 16)], cabelo)
    p.poly([(37, 11), (33, 15), (37, 16)], cabelo)
    p.r(28, 13, 30, 14, olho)
    p.r(34, 13, 36, 14, olho)
    p.p(32, 17, hexa("#c09090"))
    if pose == "rugido":
        p.r(29, 18, 35, 20, hexa("#501020"))
        p.p(30, 18, hexa("#ffffff"))
        p.p(34, 18, hexa("#ffffff"))
    else:
        p.r(30, 19, 34, 19, hexa("#802030"))
        p.p(30, 20, hexa("#ffffff"))
        p.p(34, 20, hexa("#ffffff"))
    # braços e mãos
    if pose == "cast":
        p.r(14, 12, 18, 30, capa)
        p.r(46, 12, 50, 30, capa)
        p.r(13, 8, 19, 12, pele)
        p.r(45, 8, 51, 12, pele)
        p.e(25, 0, 39, 12, hexa("#ff4020"))
        p.e(28, 3, 36, 9, hexa("#ffd060"))
    elif pose == "rugido":
        p.r(10, 18, 24, 22, capa)
        p.r(40, 18, 54, 22, capa)
        p.r(6, 16, 12, 24, pele)
        p.r(52, 16, 58, 24, pele)
    elif pose == "golpe":
        p.r(38, 30, 56, 34, capa)
        p.r(54, 28, 62, 36, pele)
        for i in range(3):
            p.l(58, 26 + i * 4, 63, 22 + i * 6, hexa("#ff6070"))
    else:
        p.r(23, 30, 27, 46, capa)
        p.r(37, 30, 41, 46, capa)
        p.r(23, 46, 27, 50, pele)
        p.r(37, 46, 41, 50, pele)
    return p


def chefe_frames():
    return [chefe(k) for k in ("idle0", "idle1", "cast", "golpe", "rugido")]


# --------------------------------------------------------------------------- PROJÉTEIS E EFEITOS


def osso_frames():
    base = Pix(12, 12)
    osso = hexa("#f0ead6")
    base.r(2, 5, 9, 6, osso)
    for (x, y) in ((1, 4), (1, 7), (10, 4), (10, 7)):
        base.r(x, y, x + 1, y + 1, osso)
    return [girar(base, a) for a in (0, 45, 90, 135)]


def bola_fogo_frames():
    fr = []
    for f in range(3):
        p = Pix(16, 16)
        p.poly([(1, 8), (7, 3 + f % 2), (7, 13 - f % 2)], hexa("#c02010"))  # cauda
        p.e(5, 3, 14, 12, hexa("#e84418"))
        p.e(6 + (f == 1), 4, 13, 11, hexa("#ff8a20"))
        p.e(8, 6, 12, 10, hexa("#ffe070"))
        fr.append(p)
    return fr


def adaga_frames():
    p = Pix(18, 8)
    p.poly([(17, 3), (6, 1), (6, 5)], hexa("#e6eefa"))
    p.l(6, 3, 16, 3, hexa("#8fa2c4"))
    p.r(3, 0, 5, 6, hexa("#d0a030"))
    p.r(0, 2, 3, 4, hexa("#5a3a20"))
    return [p]


def machado_frames():
    base = Pix(18, 18)
    base.r(8, 2, 9, 16, hexa("#7a4a24"))
    base.poly([(9, 2), (16, 1), (16, 9), (9, 8)], hexa("#cdd8e8"))
    base.poly([(9, 2), (13, 2), (13, 8), (9, 8)], hexa("#8fa2c4"))
    return [girar(base, a) for a in (0, 90, 180, 270)]


def agua_frames():
    p = Pix(10, 14)
    p.r(3, 1, 6, 3, hexa("#a0703a"))
    p.r(3, 4, 6, 5, hexa("#cfe8ff"))
    p.e(1, 5, 8, 12, hexa("#5aa8ff"))
    p.e(3, 6, 5, 8, hexa("#d8f0ff"))
    return [girar(p, a) for a in (0, 90, 180, 270)]


def chama_frames():
    rng = random.Random(7)
    fr = []
    for f in range(4):
        p = Pix(20, 28)
        for i in range(5):
            x = 2 + i * 3 + rng.randint(-1, 1)
            h = rng.randint(14, 25)
            p.poly([(x, 27), (x + 5, 27), (x + 2, 27 - h)], hexa("#e84418"))
        for i in range(4):
            x = 4 + i * 3 + rng.randint(-1, 1)
            h = rng.randint(9, 18)
            p.poly([(x, 27), (x + 4, 27), (x + 2, 27 - h)], hexa("#ff9a28"))
        p.poly([(7, 27), (13, 27), (10, 15 + f % 2 * 2)], hexa("#fff0a0"))
        fr.append(p)
    return fr


def bumerangue_frames():
    base = Pix(18, 18)
    base.poly([(2, 3), (15, 3), (15, 7), (7, 7), (7, 15), (2, 15)], hexa("#e0b040"))
    base.poly([(4, 4), (14, 4), (14, 5), (5, 5), (5, 14), (4, 14)], hexa("#fff0a0"))
    return [girar(base, a) for a in (0, 90, 180, 270)]


def pilar_fogo_frames():
    rng = random.Random(11)
    fr = []
    for f in range(4):
        p = Pix(26, 100)
        for camada, cor, larg in ((0, "#c01808", 11), (1, "#f05a10", 8), (2, "#ffb030", 5), (3, "#fff2b0", 2)):
            for y in range(99, 0, -2):
                t = (99 - y) / 99.0
                w = max(1, int(larg * (1 - t * 0.55)) + rng.randint(-1, 1))
                cx = 13 + int(math.sin(y * 0.3 + f * 1.7 + camada) * 2)
                p.r(cx - w, y, cx + w, y + 1, hexa(cor))
        fr.append(p)
    return fr


def onda_frames():
    fr = []
    for f in range(2):
        p = Pix(22, 22)
        p.poly([(2, 20), (8, 4 + f * 2), (20, 20), (14, 20), (9, 11), (6, 20)], hexa("#7a2ad0"))
        p.poly([(6, 20), (9, 9 + f * 2), (13, 20), (11, 20), (9, 14)], hexa("#d8a0ff"))
        fr.append(p)
    return fr


def golpe_frames():
    """Arco do golpe de espada (sem contorno, branco para ser tingido por arma)."""
    fr = []
    cfg = [(-68, -5, 5), (-72, 72, 8), (5, 70, 5)]
    for ini, fim, larg in cfg:
        p = Pix(44, 40)
        cx, cy, R = 3, 20, 34
        for k in range(larg):
            alpha = 255 if k > 1 else 180
            p.d.arc([cx - R + k, cy - R + k, cx + R - k, cy + R - k], ini, fim, fill=(255, 255, 255, alpha), width=1)
        for k in range(2):
            p.d.arc([cx - R - 3 - k, cy - R - 3 - k, cx + R + 3 + k, cy + R + 3 + k], ini + 6, fim - 6, fill=(255, 255, 255, 110), width=1)
        fr.append(p)
    return fr


# --------------------------------------------------------------------------- ITENS (16x16)


def itens_frames():
    cel = []

    def novo():
        return Pix(16, 16)

    # 0 coração pequeno, 1 coração grande
    H = ["..RR.RR..", ".RWRRRRR.", ".RWRRRRR.", ".RRRRRRR.", "..RRRRR..", "...RRR...", "....R...."]
    pal = {"R": hexa("#e8304a"), "W": hexa("#ff9aa8")}
    a = novo()
    bmp(a, H, pal, 3, 4)
    cel.append(a)
    b = novo()
    bmp(b, H, {"R": hexa("#d02060"), "W": hexa("#ff9ac8")}, 0, 1, 2)
    cel.append(b)
    # 2 carne
    c = novo()
    c.e(1, 5, 11, 14, hexa("#b05820"))
    c.e(2, 6, 7, 10, hexa("#d98a48"))
    c.r(10, 3, 14, 5, hexa("#f4f0e0"))
    c.r(12, 1, 14, 4, hexa("#f4f0e0"))
    c.l(11, 5, 8, 9, hexa("#f4f0e0"), 2)
    cel.append(c)
    # 3 cálice
    d = novo()
    bmp(d, ["OOOOOOOOO", "OYYYYYYYO", ".OYYYYYO.", ".OOYYYOO.", "..OOYOO..", "...OYO...", "...OYO...", "..OOOOO..", ".OYYYYYO."],
        {"O": hexa("#c08a20"), "Y": hexa("#ffe070")}, 3, 3)
    d.p(8, 5, hexa("#e03050"))
    cel.append(d)
    # 4 bolsa de ouro
    e = novo()
    e.e(2, 5, 13, 15, hexa("#6a8a3a"))
    e.r(5, 2, 10, 6, hexa("#6a8a3a"))
    e.r(4, 4, 11, 5, hexa("#e0b040"))
    e.r(7, 7, 8, 13, hexa("#f0d060"))
    e.r(6, 8, 9, 8, hexa("#f0d060"))
    e.r(6, 12, 9, 12, hexa("#f0d060"))
    cel.append(e)
    # 5 moeda
    f = novo()
    f.e(3, 3, 12, 12, hexa("#c08a20"))
    f.e(4, 4, 11, 11, hexa("#ffd84a"))
    f.r(7, 5, 8, 10, hexa("#c08a20"))
    cel.append(f)
    # 6 cruz (1UP)
    g = novo()
    g.r(7, 1, 8, 14, hexa("#ffe070"))
    g.r(3, 5, 12, 6, hexa("#ffe070"))
    g.r(7, 1, 7, 14, hexa("#fff8c0"))
    g.p(7, 5, hexa("#e03050"))
    cel.append(g)
    # 7 adaga
    h = novo()
    h.l(3, 12, 13, 3, hexa("#e6eefa"), 2)
    h.l(2, 13, 5, 10, hexa("#d0a030"), 2)
    cel.append(h)
    # 8 machado
    i = novo()
    i.l(4, 13, 11, 3, hexa("#7a4a24"), 2)
    i.poly([(8, 2), (14, 4), (13, 9), (9, 7)], hexa("#cdd8e8"))
    cel.append(i)
    # 9 água benta
    j = novo()
    j.r(6, 2, 9, 4, hexa("#a0703a"))
    j.e(3, 5, 12, 14, hexa("#5aa8ff"))
    j.e(5, 7, 7, 9, hexa("#d8f0ff"))
    cel.append(j)
    # 10 bumerangue
    k = novo()
    k.poly([(2, 3), (14, 3), (14, 7), (6, 7), (6, 14), (2, 14)], hexa("#e0b040"))
    k.poly([(4, 4), (13, 4), (13, 5), (5, 5), (5, 13), (4, 13)], hexa("#fff0a0"))
    cel.append(k)
    # 11..14 cristais de armas
    for cor in ("#9fb4d0", "#6fe39a", "#f0a040", "#e0304a"):
        m = novo()
        m.poly([(8, 0), (14, 7), (8, 15), (2, 7)], hexa(cor))
        m.poly([(8, 2), (12, 7), (8, 8), (4, 7)], hexa("#ffffff", 140))
        m.l(8, 3, 8, 11, hexa("#202030"), 1)
        m.l(6, 5, 10, 5, hexa("#202030"), 1)
        cel.append(m)
    return cel


def vela_frames():
    fr = []
    for f in range(2):
        p = Pix(14, 28)
        p.r(3, 25, 10, 27, hexa("#7a6a4a"))
        p.r(6, 12, 7, 25, hexa("#a08a4a"))
        p.r(2, 10, 11, 12, hexa("#d0aa40"))
        p.r(5, 4, 8, 10, hexa("#f4ecd0"))
        p.r(4, 0, 4, 0, (0, 0, 0, 0))
        if f == 0:
            p.poly([(6, 0), (9, 3), (7, 5), (5, 3)], hexa("#ffb030"))
            p.poly([(6, 2), (7, 3), (6, 4)], hexa("#fff0a0"))
        else:
            p.poly([(7, 0), (9, 3), (7, 5), (4, 3)], hexa("#ffb030"))
            p.poly([(7, 2), (7, 3), (6, 4)], hexa("#fff0a0"))
        fr.append(p)
    return fr


def checkpoint_frames():
    fr = []
    for f in range(3):
        p = Pix(20, 34)
        p.r(5, 28, 14, 33, hexa("#58506a"))
        p.r(3, 30, 16, 33, hexa("#6e647e"))
        p.r(7, 14, 12, 28, hexa("#6e647e"))
        p.r(3, 10, 16, 14, hexa("#8a809c"))
        p.r(2, 9, 17, 10, hexa("#aaa0bc"))
        if f == 0:
            p.r(5, 8, 14, 9, hexa("#3a3040"))
        else:
            h = 8 + (f == 2) * 2
            p.poly([(4, 9), (10, 9 - h - 4), (16, 9)], hexa("#e84418"))
            p.poly([(6, 9), (10, 9 - h), (14, 9)], hexa("#ff9a28"))
            p.poly([(8, 9), (10, 9 - h // 2), (12, 9)], hexa("#fff0a0"))
        fr.append(p)
    return fr


def porta_frames():
    fr = []
    for f in range(2):
        p = Pix(36, 68)
        pedra = hexa("#5a5070")
        p.r(0, 14, 35, 67, pedra)
        p.e(0, 0, 35, 30, pedra)
        p.r(4, 22, 31, 67, hexa("#150f22"))
        p.e(4, 6, 31, 40, hexa("#150f22"))
        luz = hexa("#9a60ff") if f == 0 else hexa("#c090ff")
        p.r(8, 26, 27, 67, luz)
        p.e(8, 10, 27, 40, luz)
        p.r(14, 30, 21, 67, hexa("#e8d0ff"))
        p.e(14, 18, 21, 40, hexa("#e8d0ff"))
        p.r(0, 60, 35, 67, hexa("#3e3650"))
        fr.append(p)
    return fr


def espinho_img():
    p = Pix(16, 16)
    for i in range(3):
        x = i * 5
        p.poly([(x, 15), (x + 5, 15), (x + 2, 3)], hexa("#aab4c8"))
        p.poly([(x + 2, 3), (x + 3, 15), (x + 5, 15)], hexa("#6e788e"))
    p.r(0, 14, 15, 15, hexa("#3e3650"))
    return p


# --------------------------------------------------------------------------- TILES (16x16)


def _ruido(rng, base, var=14):
    d = rng.randint(-var, var)
    return tuple(max(0, min(255, c + d)) for c in base[:3]) + (255,)


def tile_cemiterio(rng):
    terra = (86, 62, 48)
    grama = (62, 96, 52)
    topo = Pix(16, 16)
    miolo = Pix(16, 16)
    for y in range(16):
        for x in range(16):
            miolo.p(x, y, _ruido(rng, terra, 12))
            topo.p(x, y, _ruido(rng, terra, 12))
    for x in range(16):
        h = 4 + rng.randint(-1, 1)
        for y in range(h):
            topo.p(x, y, _ruido(rng, grama, 14))
        topo.p(x, 0, _ruido(rng, (96, 132, 70), 10))
    for _ in range(5):
        x, y = rng.randint(0, 14), rng.randint(6, 14)
        miolo.r(x, y, x + 1, y + 1, (60, 44, 36, 255))
        topo.r(x, y, x + 1, y + 1, (60, 44, 36, 255))
    return topo, miolo


def tile_tijolo(rng, cor, claro, escuro, topo_cor):
    miolo = Pix(16, 16)
    for y in range(16):
        for x in range(16):
            miolo.p(x, y, _ruido(rng, cor, 8))
    for y in (0, 8):
        miolo.r(0, y, 15, y, escuro)
    for x in (0, 8):
        miolo.r(x, 1, x, 7, escuro)
    for x in (4, 12):
        miolo.r(x, 9, x, 15, escuro)
    miolo.r(1, 1, 7, 1, claro)
    miolo.r(9, 9, 15, 9, claro)
    topo = Pix(16, 16)
    topo.img.paste(miolo.img, (0, 0))
    topo.r(0, 0, 15, 3, topo_cor)
    topo.r(0, 0, 15, 0, claro)
    topo.r(0, 3, 15, 3, escuro)
    for x in range(0, 16, 5):
        topo.r(x, 1, x, 2, escuro)
    return topo, miolo


def tile_plataforma(rng, cor, claro, escuro):
    p = Pix(16, 16)
    for y in range(16):
        for x in range(16):
            p.p(x, y, _ruido(rng, cor, 8))
    p.r(0, 0, 15, 1, claro)
    p.r(0, 14, 15, 15, escuro)
    p.r(0, 0, 0, 15, escuro)
    p.r(15, 0, 15, 15, escuro)
    p.r(3, 5, 12, 10, escuro)
    p.r(4, 6, 11, 9, tuple(max(0, c - 14) for c in cor) + (255,))
    p.p(4, 6, claro)
    p.p(11, 9, claro)
    return p


def gerar_tiles():
    rng = random.Random(3)
    topo, miolo = tile_cemiterio(rng)
    salvar(topo, "tiles", "cem_topo.png")
    salvar(miolo, "tiles", "cem_miolo.png")
    salvar(tile_plataforma(rng, (112, 112, 128), (176, 176, 196), (52, 52, 68)), "tiles", "cem_plat.png")
    topo, miolo = tile_tijolo(rng, (92, 40, 52), (150, 74, 84), (44, 18, 28), (118, 56, 68))
    salvar(topo, "tiles", "salao_topo.png")
    salvar(miolo, "tiles", "salao_miolo.png")
    salvar(tile_plataforma(rng, (132, 100, 70), (200, 164, 110), (64, 44, 30)), "tiles", "salao_plat.png")
    topo, miolo = tile_tijolo(rng, (50, 58, 86), (96, 110, 150), (24, 28, 46), (66, 78, 112))
    salvar(topo, "tiles", "torre_topo.png")
    salvar(miolo, "tiles", "torre_miolo.png")
    salvar(tile_plataforma(rng, (70, 84, 120), (130, 150, 200), (30, 36, 60)), "tiles", "torre_plat.png")


# --------------------------------------------------------------------------- DECORAÇÃO


def deco_lapide():
    p = Pix(16, 22)
    p.e(1, 0, 14, 12, hexa("#8a8aa0"))
    p.r(1, 6, 14, 21, hexa("#8a8aa0"))
    p.r(1, 6, 3, 21, hexa("#6a6a84"))
    p.r(7, 4, 8, 12, hexa("#50506a"))
    p.r(5, 6, 10, 7, hexa("#50506a"))
    return p


def deco_cruz():
    p = Pix(18, 30)
    p.r(7, 2, 10, 28, hexa("#8a8aa0"))
    p.r(2, 8, 15, 11, hexa("#8a8aa0"))
    p.r(7, 2, 8, 28, hexa("#aaaac0"))
    p.r(4, 26, 13, 29, hexa("#6a6a84"))
    return p


def deco_arvore():
    p = Pix(56, 90)
    tronco = hexa("#2a1f2e")
    p.poly([(24, 89), (32, 89), (30, 40), (26, 40)], tronco)
    for (x0, y0, x1, y1, w) in ((28, 50, 8, 28, 3), (28, 44, 50, 20, 3), (14, 36, 4, 18, 2), (40, 30, 52, 8, 2),
                                (28, 58, 46, 46, 2), (28, 40, 22, 6, 2), (8, 28, 2, 36, 1), (50, 20, 54, 28, 1)):
        p.l(x0, y0, x1, y1, tronco, w)
    return p


def deco_cerca():
    p = Pix(32, 20)
    ferro = hexa("#2e2a3c")
    for x in range(1, 32, 5):
        p.r(x, 4, x + 1, 19, ferro)
        p.poly([(x - 1, 4), (x + 1, 0), (x + 3, 4)], ferro)
    p.r(0, 9, 31, 10, ferro)
    p.r(0, 15, 31, 16, ferro)
    return p


def deco_janela():
    p = Pix(26, 52)
    pedra = hexa("#3a3248")
    p.r(0, 14, 25, 51, pedra)
    p.e(0, 0, 25, 28, pedra)
    p.r(3, 16, 22, 51, hexa("#c8a050"))
    p.e(3, 3, 22, 28, hexa("#c8a050"))
    for x in (7, 13, 18):
        p.r(x, 4, x, 49, hexa("#2a2234"))
    p.r(3, 24, 22, 25, hexa("#2a2234"))
    p.r(3, 38, 22, 39, hexa("#2a2234"))
    p.r(5, 18, 8, 23, hexa("#ffe8a0"))
    return p


def deco_janela_azul():
    p = deco_janela()
    a = p.img.copy()
    px = a.load()
    for y in range(a.height):
        for x in range(a.width):
            r, g, b, al = px[x, y]
            if (r, g, b) == (200, 160, 80):
                px[x, y] = (70, 110, 200, al)
            elif (r, g, b) == (255, 232, 160):
                px[x, y] = (170, 210, 255, al)
    p.img = a
    return p


def deco_estandarte():
    p = Pix(18, 44)
    p.r(0, 0, 17, 2, hexa("#c0a040"))
    p.poly([(1, 3), (16, 3), (16, 38), (8, 43), (1, 38)], hexa("#8a1428"))
    p.poly([(4, 6), (13, 6), (13, 33), (8, 38), (4, 33)], hexa("#b01c34"))
    p.r(8, 10, 9, 26, hexa("#e0c060"))
    p.r(5, 15, 12, 16, hexa("#e0c060"))
    return p


def deco_pilar():
    p = Pix(24, 64)
    p.r(2, 0, 21, 5, hexa("#5a506e"))
    p.r(5, 5, 18, 58, hexa("#4a4260"))
    p.r(5, 5, 8, 58, hexa("#6a6086"))
    p.r(2, 58, 21, 63, hexa("#5a506e"))
    for x in (10, 14):
        p.r(x, 6, x, 57, hexa("#3a3450"))
    return p


def deco_lustre():
    p = Pix(36, 30)
    ouro = hexa("#c0a040")
    p.r(17, 0, 18, 8, ouro)
    p.r(2, 14, 33, 15, ouro)
    p.l(18, 8, 2, 14, ouro)
    p.l(18, 8, 33, 14, ouro)
    p.poly([(6, 15), (30, 15), (18, 22)], ouro)
    for x in (3, 10, 17, 24, 31):
        p.r(x, 9, x + 1, 13, hexa("#f4ecd0"))
        p.poly([(x, 9), (x + 2, 9), (x + 1, 5)], hexa("#ffb030"))
    return p


def deco_tocha_frames():
    fr = []
    for f in range(2):
        p = Pix(12, 26)
        p.r(5, 12, 6, 24, hexa("#6a5a3a"))
        p.r(2, 10, 9, 13, hexa("#8a7a4a"))
        h = 8 + f * 2
        p.poly([(2, 10), (6, 10 - h), (9, 10)], hexa("#e84418"))
        p.poly([(4, 10), (6, 10 - h + 3), (8, 10)], hexa("#ff9a28"))
        p.poly([(5, 10), (6, 10 - h // 2), (7, 10)], hexa("#fff0a0"))
        fr.append(p)
    return fr


# --------------------------------------------------------------------------- ORQUESTRAÇÃO


def gerar_tudo():
    salvar_folha("player", heroi_frames())
    salvar_folha("zumbi", [zumbi(i) for i in range(4)])
    salvar_folha("morcego", [morcego(i) for i in range(4)])
    salvar_folha("esqueleto", [esqueleto(i) for i in range(5)])
    salvar_folha("cavaleiro", [cavaleiro(i) for i in range(6)])
    salvar_folha("medusa", [medusa(i) for i in range(2)])
    salvar_folha("fantasma", [fantasma(i) for i in range(2)])
    salvar_folha("chefe", chefe_frames())
    salvar_folha("osso", osso_frames(), contornar=True)
    salvar_folha("bola_fogo", bola_fogo_frames(), contornar=False)
    salvar_folha("adaga", adaga_frames())
    salvar_folha("machado", machado_frames())
    salvar_folha("agua", agua_frames())
    salvar_folha("chama", chama_frames(), contornar=False)
    salvar_folha("bumerangue", bumerangue_frames())
    salvar_folha("pilar_fogo", pilar_fogo_frames(), contornar=False)
    salvar_folha("onda", onda_frames(), contornar=False)
    salvar_folha("golpe", golpe_frames(), contornar=False)
    salvar_folha("itens", itens_frames())
    salvar_folha("vela", vela_frames())
    salvar_folha("checkpoint", checkpoint_frames())
    salvar_folha("porta", porta_frames(), contornar=False)
    salvar_folha("tocha", deco_tocha_frames())
    salvar(espinho_img(), "tiles", "espinho.png")
    gerar_tiles()
    for nome, fn in (("lapide", deco_lapide), ("cruz", deco_cruz), ("arvore", deco_arvore), ("cerca", deco_cerca),
                     ("janela", deco_janela), ("janela_azul", deco_janela_azul), ("estandarte", deco_estandarte),
                     ("pilar", deco_pilar), ("lustre", deco_lustre)):
        salvar(_com_contorno(fn()), "deco", nome + ".png")


def _com_contorno(p):
    from .pix import contorno
    return contorno(p.img)

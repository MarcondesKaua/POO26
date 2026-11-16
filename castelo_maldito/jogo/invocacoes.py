"""Ataques da 2ª etapa do chefe: enxame de gafanhotos e a cruz de fogo.

Nada aqui depende de arquivos em assets/: os gafanhotos são desenhados por código (Pillow) na primeira vez que
aparecem e a cruz é desenhada com retângulos.
"""
import math
import random

import arcade
from PIL import Image

from . import ui
from .config import DIREITA, ESQUERDA
from .corpo import CorpoGrade
from .projeteis import BolaFogo

# --------------------------------------------------------------------------------------------- gafanhotos
_PALETA = {
    "k": (28, 36, 14, 255),      # contorno
    "g": (118, 166, 48, 255),    # corpo
    "G": (172, 212, 84, 255),    # brilho
    "b": (92, 62, 30, 255),      # patas
    "w": (214, 238, 168, 200),   # asas
    "e": (214, 44, 44, 255),     # olho
}

_CORPO = [
    "..............",
    "..............",
    "..kkkkkk.kkk..",
    ".kggGGggkkggk.",
    "kggggggggggGek",
    ".kkgggggggkkk.",
    "..bkbkkkkbkb..",
    ".b..b....b..b.",
]
_ASAS_CIMA = {0: "....wwww......", 1: "...wwwwww....."}
_ASAS_BAIXO = {1: "..wwwwwww....."}

_texturas = None


def _desenhar(asas):
    """Um quadro 14x8 (ampliado 2x) olhando para a direita."""
    linhas = [list(l) for l in _CORPO]
    for y, l in asas.items():
        for x, ch in enumerate(l):
            if ch != "." and linhas[y][x] == ".":
                linhas[y][x] = ch
    img = Image.new("RGBA", (14, 8), (0, 0, 0, 0))
    for y, l in enumerate(linhas):
        for x, ch in enumerate(l):
            if ch in _PALETA:
                img.putpixel((x, y), _PALETA[ch])
    return img.resize((28, 16), Image.NEAREST)


def texturas_gafanhoto():
    """(quadros_direita, quadros_esquerda) — cache em memória."""
    global _texturas
    if _texturas is None:
        dir_ = [_desenhar(_ASAS_CIMA), _desenhar(_ASAS_BAIXO)]
        esq = [im.transpose(Image.FLIP_LEFT_RIGHT) for im in dir_]
        _texturas = ([arcade.Texture(im) for im in dir_], [arcade.Texture(im) for im in esq])
    return _texturas


class Gafanhoto(CorpoGrade):
    """Inimigo de 1 de vida que cruza a arena voando. Morre com um golpe (e pode soltar item)."""

    meia_l = 13
    meia_a = 8
    hp = 1
    dano_contato = 2
    pontos = 50

    def __init__(self, x, y, direcao, vel):
        d, e = texturas_gafanhoto()
        self.quadros = d if direcao == DIREITA else e
        super().__init__(self.quadros[0], x, y)
        self.sinal = 1 if direcao == DIREITA else -1
        self.virado = direcao
        self.vel = vel
        self.y0 = y
        self.fase = random.uniform(0, 6.28)
        self.i = 0
        self.t_anim = 0.0
        self.hp_atual = 1
        self.morreu = False

    def receber_dano(self, dano, origem_x, empurrao=0):
        self.morreu = True
        return "morto"

    def ia(self, dt, jogo):
        self.fase += dt * 7
        self.center_x += self.vel * self.sinal
        self.center_y = self.y0 + math.sin(self.fase) * 14
        self.t_anim += dt
        if self.t_anim >= 0.07:
            self.t_anim = 0.0
            self.i = 1 - self.i
            self.texture = self.quadros[self.i]
        if self.center_x < -60 or self.center_x > jogo.mapa.largura_px + 60:
            self.remove_from_sprite_lists()


# --------------------------------------------------------------------------------------------- cruz de fogo
class CruzFogo:
    """Cruz de fogo no meio da arena: avisa (contorno vermelho piscando) e depois queima.

    Não é um Sprite: o jogo a guarda em TelaJogo.perigos e usa .ia(), .desenhar(), .caixas e .ativo.
    """

    dano = 4

    def __init__(self, cx, y_chao, nivel=0):
        self.cx = cx
        self.origem_x = cx
        self.nivel = nivel
        self.aviso = (1.5, 1.3, 1.1)[nivel]
        self.duracao = 1.3
        self.t = 0.0
        self.acendeu = False
        self.morreu = False
        self.fagulha = 0.0
        # braço vertical (do chão para cima) e horizontal (na altura do corpo: é preciso pular ou usar o dash)
        self.vertical = (cx - 22, y_chao, cx + 22, y_chao + 270)
        self.horizontal = (cx - 220, y_chao + 40, cx + 220, y_chao + 80)
        self.caixas = [self.vertical, self.horizontal]

    @property
    def ativo(self):
        return self.aviso <= self.t < self.aviso + self.duracao

    def ia(self, dt, jogo):
        self.t += dt
        if not self.acendeu and self.t >= self.aviso:
            self.acendeu = True
            jogo.audio.tocar("fogo")
            jogo.tremer(0.35)
            if self.nivel >= 1:
                # a cruz solta 4 bolas de fogo em diagonal ao acender
                cx, cy = self.cx, self.vertical[1] + 170
                for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                    jogo.projeteis_inimigos.append(BolaFogo(cx, cy, 3.6 * sx, 3.6 * sy))
        if self.ativo:
            self.fagulha -= dt
            if self.fagulha <= 0:
                self.fagulha = 0.05
                x = random.uniform(self.vertical[0], self.vertical[2]) if random.random() < 0.5 \
                    else random.uniform(self.horizontal[0], self.horizontal[2])
                y = random.uniform(self.vertical[1], self.vertical[3])
                jogo.efeitos.faiscas(x, y, (255, 170, 60, 255), 1, 1.5, 0.45, -0.05)
        if self.t >= self.aviso + self.duracao:
            self.morreu = True

    def desenhar(self):
        if self.t < self.aviso:
            pulso = int(50 + 90 * abs(math.sin(self.t * 9)))
            for (l, b, r, t) in self.caixas:
                ui.retangulo(l, b, r - l, t - b, (255, 40, 40, pulso))
                ui.contorno(l, b, r - l, t - b, (255, 110, 110, 255), 2)
            return
        resto = self.aviso + self.duracao - self.t
        a = int(255 * min(1.0, resto / 0.25))
        for (l, b, r, t) in self.caixas:
            ui.retangulo(l, b, r - l, t - b, (240, 80, 20, a))
            ui.retangulo(l + 4, b + 4, r - l - 8, t - b - 8, (255, 170, 50, a))
            n = 3 + int(random.random() * 3)
            ui.retangulo(l + 9, b + 9, max(2, r - l - 18), max(2, t - b - 18), (255, 240, 170, a))
            ui.retangulo(l + 4, b + 4 + n, max(2, r - l - 8), 2, (255, 120, 30, a))

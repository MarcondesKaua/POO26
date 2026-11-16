"""Utilitários de colisão por grade (usados por inimigos, itens e projéteis) e caixas AABB."""
import arcade

from .config import TILE


def sobrepoe(a, b):
    """a, b = (esq, baixo, dir, topo)."""
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]


def sinal(v):
    return (v > 0) - (v < 0)


class CorpoGrade(arcade.Sprite):
    """Sprite com caixa de colisão própria que anda sobre a grade de blocos do mapa."""

    meia_l = 12
    meia_a = 20

    def __init__(self, textura, x, y):
        super().__init__(textura, scale=1.0, center_x=x, center_y=y)
        self.vy = 0.0
        self.no_chao = False
        self.bateu_x = False

    @property
    def caixa(self):
        return (self.center_x - self.meia_l, self.center_y - self.meia_a,
                self.center_x + self.meia_l, self.center_y + self.meia_a)

    def mover_grade(self, mapa, dx, dy):
        self.bateu_x = False
        self.no_chao = False
        self.center_x += dx
        l, b, r, t = self.caixa
        if dx and mapa.colide(l, b, r, t):
            self.bateu_x = True
            if dx > 0:
                self.center_x = int((r - 0.01) // TILE) * TILE - self.meia_l - 0.01
            else:
                self.center_x = (int(l // TILE) + 1) * TILE + self.meia_l + 0.01
        self.center_y += dy
        l, b, r, t = self.caixa
        if dy and mapa.colide(l, b, r, t):
            if dy < 0:
                self.center_y = (int(b // TILE) + 1) * TILE + self.meia_a + 0.01
                self.no_chao = True
            else:
                self.center_y = int((t - 0.01) // TILE) * TILE - self.meia_a - 0.01
            self.vy = 0.0

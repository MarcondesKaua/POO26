"""Blocos do cenário (chão, paredes e plataformas suspensas) e espinhos."""
import arcade

from . import recursos
from .config import TILE


class Bloco(arcade.Sprite):
    """Um tile sólido. tipo: 'topo' (superfície), 'miolo' (preenchimento) ou 'plat' (plataforma suspensa)."""

    def __init__(self, tema, tipo, coluna, linha):
        tex = recursos.textura("tiles", f"{tema}_{tipo}.png", caixa=True)
        super().__init__(tex, scale=1.0, center_x=coluna * TILE + TILE / 2, center_y=linha * TILE + TILE / 2)
        self.tipo = tipo
        self.coluna = coluna
        self.linha = linha


class Espinho(arcade.Sprite):
    """Perigo no chão: causa dano ao toque (não é sólido)."""

    def __init__(self, coluna, linha):
        super().__init__(recursos.textura("tiles", "espinho.png"), scale=1.0,
                         center_x=coluna * TILE + TILE / 2, center_y=linha * TILE + TILE / 2)

    @property
    def caixa(self):
        return (self.center_x - 13, self.center_y - 16, self.center_x + 13, self.center_y + 2)

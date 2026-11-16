"""Itens coletáveis, velas quebráveis, checkpoints e a porta de saída."""
import arcade

from . import recursos
from .config import LARGURA, TILE
from .corpo import CorpoGrade

# tipo -> (quadro na folha de itens, nome para mensagens)
TIPOS_ITEM = {
    "coracao": (0, "+1 coração"),
    "coracao_g": (1, "+5 corações"),
    "carne": (2, "Vida restaurada"),
    "calice": (3, "Cálice sagrado"),
    "bolsa": (4, "Bolsa de ouro"),
    "moeda": (5, "Moeda"),
    "cruz": (6, "1UP"),
    "adaga": (7, "Adaga"),
    "machado": (8, "Machado"),
    "agua": (9, "Água Benta"),
    "bumerangue": (10, "Bumerangue"),
    "arma1": (12, "Lâmina Veloz"),
    "arma2": (13, "Sabre do Sol"),
    "arma3": (14, "Presa Rubra"),
}


class Item(CorpoGrade):
    meia_l = 14
    meia_a = 14

    def __init__(self, tipo, x, y, vy=0.0, permanente=False):
        self.tipo = tipo
        tex = recursos.quadros("sprites/itens")[0][TIPOS_ITEM[tipo][0]]
        super().__init__(tex, x, y)
        self.vy = vy
        self.tempo = 0.0
        self.permanente = permanente or tipo.startswith("arma")
        self.morreu = False
        # sub-arma largada pelo jogador ao trocar: fica no chão até sair da tela
        self.soltado = False
        # enquanto o jogador ainda está em cima do item largado, ele não pode ser pego de volta
        self.travado = False
        self.avisado = False

    def ia(self, dt, jogo):
        self.tempo += dt
        self.vy = max(self.vy - 0.5, -12)
        self.mover_grade(jogo.mapa, 0, self.vy)
        if self.no_chao:
            self.vy = 0
        if self.soltado:
            if abs(self.center_x - jogo.cam_x) > LARGURA / 2 + 48:   # saiu da tela -> some
                self.morreu = True
        elif not self.permanente and self.tempo > 12:
            self.morreu = True
        elif not self.permanente and self.tempo > 8:
            self.alpha = 90 if int(self.tempo * 8) % 2 else 255
        if self.center_y < -100:
            self.morreu = True


class Vela(arcade.Sprite):
    """Vela quebrável: ao ser atingida solta um item."""

    def __init__(self, x, y_pes, drop):
        self.quadros = recursos.quadros("sprites/vela")[0]
        super().__init__(self.quadros[0], scale=1.0, center_x=x, center_y=y_pes + 28)
        self.drop = drop
        self.t = 0.0
        self.i = 0
        self.morreu = False

    @property
    def caixa(self):
        return (self.center_x - 12, self.center_y - 28, self.center_x + 12, self.center_y + 28)

    def ia(self, dt, jogo):
        self.t += dt
        if self.t > 0.18:
            self.t = 0
            self.i = 1 - self.i
            self.texture = self.quadros[self.i]


class Checkpoint(arcade.Sprite):
    def __init__(self, x, y_pes):
        self.quadros = recursos.quadros("sprites/checkpoint")[0]
        super().__init__(self.quadros[0], scale=1.0, center_x=x, center_y=y_pes + 34)
        self.ativo = False
        self.t = 0.0
        self.i = 1

    @property
    def caixa(self):
        return (self.center_x - 20, self.center_y - 34, self.center_x + 20, self.center_y + 34)

    def ativar(self):
        self.ativo = True

    def ia(self, dt, jogo):
        if not self.ativo:
            return
        self.t += dt
        if self.t > 0.15:
            self.t = 0
            self.i = 1 if self.i == 2 else 2
            self.texture = self.quadros[self.i]


class Porta(arcade.Sprite):
    def __init__(self, x, y_pes):
        self.quadros = recursos.quadros("sprites/porta")[0]
        super().__init__(self.quadros[0], scale=1.0, center_x=x, center_y=y_pes + 68)
        self.t = 0.0
        self.i = 0

    @property
    def caixa(self):
        return (self.center_x - 16, self.center_y - 68, self.center_x + 16, self.center_y + 40)

    def ia(self, dt, jogo):
        self.t += dt
        if self.t > 0.3:
            self.t = 0
            self.i = 1 - self.i
            self.texture = self.quadros[self.i]

"""Projéteis, poças de fogo e pilares: tanto do jogador (sub-armas) quanto dos inimigos."""
import math

import arcade

from . import recursos
from .config import DIREITA, ESQUERDA, TILE
from .corpo import sinal


class Projetil(arcade.Sprite):
    """Projétil genérico animado. Movimento em px/frame; colide com a grade de blocos."""

    def __init__(self, chave, x, y, vx, vy=0.0, dano=1, grav=0.0, hostil=False, vida=4.0, atravessa=False,
                 periodo=0.08, meia=None, bate_no_chao=False):
        direita, esquerda = recursos.quadros(chave)
        self.quadros = direita if vx >= 0 else esquerda
        super().__init__(self.quadros[0], scale=1.0, center_x=x, center_y=y)
        self.vx, self.vy = vx, vy
        self.dano = dano
        self.grav = grav
        self.hostil = hostil
        self.vida = vida
        self.atravessa = atravessa
        self.periodo = periodo
        self.t_anim = 0.0
        self.i = 0
        w, h = recursos.tamanho_quadro(chave)
        self.meia = meia or (w / 2 - 2, h / 2 - 2)
        self.atingidos = set()
        self.morreu = False
        self.bate_no_chao = bate_no_chao

    @property
    def caixa(self):
        return (self.center_x - self.meia[0], self.center_y - self.meia[1],
                self.center_x + self.meia[0], self.center_y + self.meia[1])

    def animar(self, dt):
        self.t_anim += dt
        if self.t_anim >= self.periodo:
            self.t_anim = 0.0
            self.i = (self.i + 1) % len(self.quadros)
            self.texture = self.quadros[self.i]

    def ia(self, dt, jogo):
        self.vida -= dt
        self.vy -= self.grav
        self.center_x += self.vx
        self.center_y += self.vy
        self.animar(dt)
        if self.vida <= 0:
            self.morreu = True
            return
        if jogo.mapa.colide(*self.caixa):
            self.ao_bater(jogo)

    def ao_bater(self, jogo):
        self.morreu = True

    def ao_acertar(self, jogo):
        if not self.atravessa:
            self.morreu = True


class Bumerangue(Projetil):
    def __init__(self, x, y, direcao, jogador):
        super().__init__("sprites/bumerangue", x, y, 9 * (1 if direcao == DIREITA else -1), 0, dano=3,
                         atravessa=True, vida=6.0, periodo=0.05)
        self.jogador = jogador
        self.volta = False
        self.origem = x
        self.alcance = 240

    def ia(self, dt, jogo):
        self.animar(dt)
        self.vida -= dt
        if not self.volta:
            self.center_x += self.vx
            if abs(self.center_x - self.origem) >= self.alcance or jogo.mapa.colide(*self.caixa):
                self.volta = True
                self.atingidos.clear()
        else:
            dx = self.jogador.center_x - self.center_x
            dy = self.jogador.center_y - self.center_y
            d = math.hypot(dx, dy) or 1
            self.center_x += dx / d * 11
            self.center_y += dy / d * 11
            if d < 26:
                self.morreu = True
        if self.vida <= 0:
            self.morreu = True

    def ao_bater(self, jogo):
        self.volta = True


class Agua(Projetil):
    def __init__(self, x, y, direcao):
        s = 1 if direcao == DIREITA else -1
        super().__init__("sprites/agua", x, y, 5 * s, 6, dano=1, grav=0.45, periodo=0.06, atravessa=False)

    def ao_bater(self, jogo):
        self.morreu = True
        jogo.criar_chama(self.center_x, self.center_y)
        jogo.audio.tocar("vidro")

    def ao_acertar(self, jogo):
        self.ao_bater(jogo)


class Chama(arcade.Sprite):
    """Poça de fogo da água benta: fere inimigos que a tocam."""

    def __init__(self, x, y_chao):
        direita, _ = recursos.quadros("sprites/chama")
        self.quadros = direita
        super().__init__(direita[0], scale=1.0, center_x=x, center_y=y_chao + 28)
        self.vida = 3.0
        self.t_anim = 0.0
        self.i = 0
        self.morreu = False
        self.recarga = {}

    @property
    def caixa(self):
        return (self.center_x - 16, self.center_y - 28, self.center_x + 16, self.center_y + 10)

    def ia(self, dt, jogo):
        self.vida -= dt
        self.t_anim += dt
        if self.t_anim >= 0.08:
            self.t_anim = 0
            self.i = (self.i + 1) % len(self.quadros)
            self.texture = self.quadros[self.i]
        if self.vida <= 0:
            self.morreu = True


class Osso(Projetil):
    def __init__(self, x, y, direcao):
        s = 1 if direcao == DIREITA else -1
        super().__init__("sprites/osso", x, y, 3.2 * s, 9, dano=2, grav=0.4, hostil=True, periodo=0.06, vida=3.0,
                         meia=(9, 9))


class BolaFogo(Projetil):
    def __init__(self, x, y, vx, vy):
        super().__init__("sprites/bola_fogo", x, y, vx, vy, dano=3, hostil=True, periodo=0.07, vida=5.0, meia=(12, 12))

    def ao_bater(self, jogo):
        self.morreu = True
        jogo.audio.tocar("explosao", 0.5)


class Onda(Projetil):
    """Onda roxa que desliza pelo chão."""

    def __init__(self, x, y, direcao):
        s = 1 if direcao == DIREITA else -1
        super().__init__("sprites/onda", x, y, 5.5 * s, 0, dano=3, hostil=True, periodo=0.1, vida=6.0, meia=(16, 18))

    def ia(self, dt, jogo):
        self.vida -= dt
        self.center_x += self.vx
        self.animar(dt)
        if self.vida <= 0 or self.center_x < 0 or self.center_x > jogo.mapa.largura_px:
            self.morreu = True


class Pilar(arcade.Sprite):
    """Pilar de fogo do chefe: aviso (linha vermelha) e depois erupção."""

    dano = 4
    atravessa = True
    hostil = True

    def __init__(self, x, y_chao):
        direita, _ = recursos.quadros("sprites/pilar_fogo")
        self.quadros = direita
        super().__init__(direita[0], scale=1.0, center_x=x, center_y=y_chao + 100)
        self.aviso = 1.0
        self.ativo = 0.9
        self.i = 0
        self.t_anim = 0.0
        self.morreu = False
        self.tocou_som = False
        self.alpha = 0

    @property
    def perigoso(self):
        return self.aviso <= 0

    @property
    def caixa(self):
        return (self.center_x - 18, self.center_y - 100, self.center_x + 18, self.center_y + 100)

    def ia(self, dt, jogo):
        if self.aviso > 0:
            self.aviso -= dt
            if self.aviso <= 0:
                jogo.audio.tocar("fogo")
                self.alpha = 255
                jogo.tremer(0.25)
        else:
            self.ativo -= dt
            self.t_anim += dt
            if self.t_anim > 0.07:
                self.t_anim = 0
                self.i = (self.i + 1) % len(self.quadros)
                self.texture = self.quadros[self.i]
            if self.ativo <= 0:
                self.morreu = True

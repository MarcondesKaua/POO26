"""Inimigos comuns. Cada classe herda de Inimigo e implementa sua própria IA em ia(dt, jogo)."""
import math
import random

from . import recursos
from .config import DIREITA, ESQUERDA
from .corpo import CorpoGrade, sinal
from .projeteis import Osso


class Inimigo(CorpoGrade):
    chave = "sprites/zumbi"
    hp = 4
    dano_contato = 2
    pontos = 100
    vel = 1.0
    gravidade = True

    def __init__(self, x, y_pes):
        self.quadros = recursos.quadros(self.chave)
        w, h = recursos.tamanho_quadro(self.chave)
        self.meia_l = w / 2 - 6
        self.meia_a = h / 2 - 2
        super().__init__(self.quadros[0][0], x, y_pes + self.meia_a + 1)
        self.virado = ESQUERDA
        self.i = 0
        self.t_anim = 0.0
        self.hp_atual = self.hp
        self.flash = 0.0
        self.morreu = False
        self.tempo = 0.0
        self.definir_quadro(0)

    def definir_quadro(self, i):
        self.i = i
        self.texture = self.quadros[self.virado][i]

    def animar(self, dt, indices, periodo=0.14):
        self.t_anim += dt
        if self.t_anim >= periodo:
            self.t_anim -= periodo
            self.i_ciclo = (getattr(self, "i_ciclo", -1) + 1) % len(indices)
        self.definir_quadro(indices[getattr(self, "i_ciclo", 0) % len(indices)])

    def virar_para(self, alvo_x):
        self.virado = DIREITA if alvo_x >= self.center_x else ESQUERDA

    def receber_dano(self, dano, origem_x, empurrao=0):
        """Retorna 'morto', 'ferido' ou 'bloqueado'."""
        self.hp_atual -= dano
        self.flash = 0.12
        self.color = (255, 120, 120, 255)
        if empurrao and self.gravidade:
            self.mover_grade_seguro(sinal(self.center_x - origem_x) * empurrao)
        if self.hp_atual <= 0:
            self.morreu = True
            return "morto"
        return "ferido"

    def mover_grade_seguro(self, dx):
        if getattr(self, "mapa", None) is not None:
            self.mover_grade(self.mapa, dx, 0)

    def passo_comum(self, dt):
        self.tempo += dt
        if self.flash > 0:
            self.flash -= dt
            if self.flash <= 0:
                self.color = (255, 255, 255, 255)

    def ia(self, dt, jogo):
        self.mapa = jogo.mapa
        self.passo_comum(dt)

    def cair(self, jogo):
        self.vy = max(self.vy - 0.6, -14)
        self.mover_grade(jogo.mapa, 0, self.vy)

    def pe_a_frente_seguro(self, jogo, dist=6):
        l, b, r, t = self.caixa
        x = r + dist if self.virado == DIREITA else l - dist
        return jogo.mapa.solido_em(x, b - 4)


class Zumbi(Inimigo):
    chave = "sprites/zumbi"
    hp = 4
    pontos = 100
    vel = 1.1

    def ia(self, dt, jogo):
        super().ia(dt, jogo)
        self.cair(jogo)
        if self.no_chao:
            self.mover_grade(jogo.mapa, self.vel * (1 if self.virado == DIREITA else -1), 0)
            if self.bateu_x:
                self.virado = DIREITA if self.virado == ESQUERDA else ESQUERDA
        self.animar(dt, (0, 1, 2, 3), 0.18)


class Morcego(Inimigo):
    chave = "sprites/morcego"
    hp = 2
    pontos = 150
    gravidade = False

    def __init__(self, x, y_pes):
        super().__init__(x, y_pes)
        self.centro_y = self.center_y
        self.estado = "dormindo"
        self.fase = random.random() * 6
        self.meia_l = 14
        self.meia_a = 10
        self.definir_quadro(3)

    def ia(self, dt, jogo):
        super().ia(dt, jogo)
        p = jogo.jogador
        if self.estado == "dormindo":
            self.definir_quadro(3)
            if abs(p.center_x - self.center_x) < 300 and abs(p.center_y - self.center_y) < 260:
                self.estado = "voando"
        else:
            self.fase += dt * 5
            self.virar_para(p.center_x)
            dx = p.center_x - self.center_x
            alvo_y = p.center_y + 10 + math.sin(self.fase) * 40
            self.center_x += sinal(dx) * min(abs(dx), 2.6)
            self.center_y += max(-2.2, min(2.2, alvo_y - self.center_y))
            self.animar(dt, (0, 1, 2, 1), 0.09)


class Esqueleto(Inimigo):
    chave = "sprites/esqueleto"
    hp = 6
    pontos = 200
    vel = 0.9

    def __init__(self, x, y_pes):
        super().__init__(x, y_pes)
        self.recarga = random.uniform(1.0, 2.0)
        self.arremesso = 0.0

    def ia(self, dt, jogo):
        super().ia(dt, jogo)
        self.cair(jogo)
        p = jogo.jogador
        dx = p.center_x - self.center_x
        perto = abs(dx) < 420 and abs(p.center_y - self.center_y) < 140
        if self.arremesso > 0:
            self.arremesso -= dt
            self.definir_quadro(4)
            if self.arremesso <= 0:
                jogo.projeteis_inimigos.append(Osso(self.center_x, self.center_y + 22, self.virado))
                jogo.audio.tocar("osso", 0.7)
            return
        if perto:
            self.virar_para(p.center_x)
            d = abs(dx)
            passo = 0
            if d > 260:
                passo = self.vel
            elif d < 150:
                passo = -self.vel * 0.8
            if passo and self.no_chao:
                lado = (1 if self.virado == DIREITA else -1) * (1 if passo > 0 else -1)
                l, b, r, t = self.caixa
                x_pe = (r + 6) if lado > 0 else (l - 6)
                if jogo.mapa.solido_em(x_pe, b - 4):
                    self.mover_grade(jogo.mapa, lado * abs(passo), 0)
            self.recarga -= dt
            if self.recarga <= 0:
                self.recarga = random.uniform(1.6, 2.6)
                self.arremesso = 0.35
            self.animar(dt, (0, 1, 2, 3), 0.18)
        else:
            self.definir_quadro(1)


class Cavaleiro(Inimigo):
    chave = "sprites/cavaleiro"
    hp = 14
    dano_contato = 3
    pontos = 400
    vel = 0.8
    JANELA_RECUP = 0.45   # segundos vulnerável logo após o golpe (aumente para facilitar)

    def __init__(self, x, y_pes):
        super().__init__(x, y_pes)
        self.ataque = None   # (fase, t)
        self.recarga = 1.0
        self.dir_patrulha = ESQUERDA

    @property
    def atacando(self):
        return self.ataque is not None

    def caixa_golpe(self):
        if self.ataque and self.ataque[0] == "golpe":
            x = self.center_x + (self.meia_l if self.virado == DIREITA else -self.meia_l)
            if self.virado == DIREITA:
                return (x, self.center_y - 40, x + 66, self.center_y + 10)
            return (x - 66, self.center_y - 40, x, self.center_y + 10)
        return None

    def receber_dano(self, dano, origem_x, empurrao=0):
        frente = (origem_x > self.center_x) == (self.virado == DIREITA)
        if frente and not self.atacando:
            self.flash = 0.0
            return "bloqueado"
        return super().receber_dano(dano, origem_x, 0)

    def ia(self, dt, jogo):
        super().ia(dt, jogo)
        self.cair(jogo)
        p = jogo.jogador
        dx = p.center_x - self.center_x
        if self.ataque:
            fase, t = self.ataque
            t += dt
            if fase == "prep":
                self.definir_quadro(4)
                if t >= 0.5:
                    fase, t = "golpe", 0.0
                    jogo.audio.tocar("golpe_pesado", 0.6)
            elif fase == "golpe":
                self.definir_quadro(5)
                if t >= 0.2:
                    fase, t = "recup", 0.0   # depois do golpe ele fica exposto (escudo baixo) por um instante
            elif fase == "recup":
                self.definir_quadro(5)
                if t >= self.JANELA_RECUP:
                    self.ataque = None
                    self.recarga = 1.4
                    return
            self.ataque = (fase, t)
            return
        self.recarga -= dt
        ativo = abs(dx) < 380 and abs(p.center_y - self.center_y) < 120
        if ativo:
            self.virar_para(p.center_x)
            if abs(dx) < 100 and self.recarga <= 0:
                self.ataque = ("prep", 0.0)
                return
            if abs(dx) > 70 and self.no_chao and self.pe_a_frente_seguro(jogo):
                self.mover_grade(jogo.mapa, self.vel * 1.3 * (1 if self.virado == DIREITA else -1), 0)
        else:
            self.virado = self.dir_patrulha
            if self.no_chao and self.pe_a_frente_seguro(jogo):
                self.mover_grade(jogo.mapa, self.vel * 0.6 * (1 if self.virado == DIREITA else -1), 0)
            if self.bateu_x or not self.pe_a_frente_seguro(jogo):
                self.dir_patrulha = DIREITA if self.dir_patrulha == ESQUERDA else ESQUERDA
        self.animar(dt, (0, 1, 2, 3), 0.22)


class Medusa(Inimigo):
    chave = "sprites/medusa"
    hp = 2
    pontos = 100
    gravidade = False

    def __init__(self, x, y_pes):
        super().__init__(x, y_pes)
        self.meia_l = 14
        self.meia_a = 14
        self.y0 = self.center_y
        self.fase = random.random() * 6
        self.dir = -1

    def ia(self, dt, jogo):
        super().ia(dt, jogo)
        self.fase += dt * 4.5
        self.center_x += 2.8 * self.dir
        self.center_y = self.y0 + math.sin(self.fase) * 50
        self.virado = DIREITA if self.dir > 0 else ESQUERDA
        self.animar(dt, (0, 1), 0.15)


class Fantasma(Inimigo):
    chave = "sprites/fantasma"
    hp = 5
    dano_contato = 3
    pontos = 300
    gravidade = False

    def __init__(self, x, y_pes):
        super().__init__(x, y_pes)
        self.meia_l = 14
        self.meia_a = 24

    def ia(self, dt, jogo):
        super().ia(dt, jogo)
        p = jogo.jogador
        encarado = (p.center_x < self.center_x and p.virado_para == DIREITA) or \
                   (p.center_x > self.center_x and p.virado_para == ESQUERDA)
        self.virar_para(p.center_x)
        dist = math.hypot(p.center_x - self.center_x, p.center_y - self.center_y)
        if dist < 520 and not encarado:
            d = dist or 1
            self.center_x += (p.center_x - self.center_x) / d * 1.5
            self.center_y += (p.center_y - self.center_y) / d * 1.5
            self.alpha = 235
        else:
            self.alpha = 110
        self.animar(dt, (0, 1), 0.3)


FABRICA = {
    "zumbi": Zumbi, "morcego": Morcego, "esqueleto": Esqueleto,
    "cavaleiro": Cavaleiro, "medusa": Medusa, "fantasma": Fantasma,
}

DROPS = {"zumbi": 0.25, "morcego": 0.25, "esqueleto": 0.35, "cavaleiro": 0.7, "medusa": 0.2, "fantasma": 0.5}

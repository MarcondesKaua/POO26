"""Mapa da fase: grade de tiles e listas de entidades, montados por uma API de 'construção'.

Convenção: linha r ocupa y em [r*32, (r+1)*32]. Entidades são posicionadas pela linha onde ficam os PÉS
(ex.: sobre um chão de altura 3, os pés ficam na linha 3).
"""
import random

import arcade

from . import recursos
from .bloco import Bloco, Espinho
from .config import TILE


class Mapa:
    def __init__(self, tema_tiles, tema_fundo, nome, musica, colunas, linhas=18):
        self.tema_tiles = tema_tiles
        self.tema_fundo = tema_fundo
        self.nome = nome
        self.musica = musica
        self.colunas = colunas
        self.linhas = linhas
        self.grade = {}
        self.espinhos = []
        self.velas = []          # (col, linha, drop)
        self.checkpoints = []    # (col, linha)
        self.inicio = (3, 3)
        self.porta = None
        self.inimigos = []       # (tipo, col, linha)
        self.zonas = []          # (tipo, col0, col1)
        self.itens = []          # (tipo, col, linha)
        self.decos = []          # (nome, x, y_base, ancora)
        self.chefe = None        # (col, linha)
        self.corrida = None      # None ou dict(fim=coluna da linha de chegada, dodo=(col, linha) da largada do Dodo)
        self.mult_vel = 1.0      # multiplicador da velocidade do jogador nesta fase
        self._set_espinhos = None
        self.tochas = []         # (x, y)

    # ------------------------------------------------------------ construção
    def chao(self, c0, c1, h):
        for c in range(c0, c1):
            for r in range(h):
                self.grade[(c, r)] = "solido"

    def massa(self, c, r, w, h):
        for cc in range(c, c + w):
            for rr in range(r, r + h):
                self.grade[(cc, rr)] = "solido"

    def plataforma(self, c, r, n=3):
        for cc in range(c, c + n):
            self.grade[(cc, r)] = "plat"

    def espinhos_em(self, c0, c1, r):
        for c in range(c0, c1):
            self.espinhos.append((c, r))

    def vela(self, c, r, drop=None):
        self.velas.append((c, r, drop))

    def checkpoint(self, c, r):
        self.checkpoints.append((c, r))

    def largada(self, c, r):
        self.inicio = (c, r)

    def porta_em(self, c, r):
        self.porta = (c, r)

    def inimigo(self, tipo, c, r):
        self.inimigos.append((tipo, c, r))

    def zona(self, tipo, c0, c1):
        self.zonas.append((tipo, c0, c1))

    def item(self, tipo, c, r):
        self.itens.append((tipo, c, r))

    def tocha(self, c, r):
        self.tochas.append((c * TILE + TILE / 2, r * TILE))

    def deco(self, nome, c, r, ancora="base"):
        self.decos.append((nome, c * TILE + TILE / 2, r * TILE, ancora))

    # ------------------------------------------------------------ consulta
    @property
    def largura_px(self):
        return self.colunas * TILE

    def solido(self, c, r):
        return (c, r) in self.grade

    def colide(self, l, b, r, t):
        c0, c1 = int(l // TILE), int((r - 0.001) // TILE)
        r0, r1 = int(b // TILE), int((t - 0.001) // TILE)
        for c in range(c0, c1 + 1):
            for rr in range(r0, r1 + 1):
                if (c, rr) in self.grade:
                    return True
        return False

    def solido_em(self, x, y):
        return (int(x // TILE), int(y // TILE)) in self.grade

    def espinho_em(self, x, y):
        if self._set_espinhos is None:
            self._set_espinhos = set(self.espinhos)
        return (int(x // TILE), int(y // TILE)) in self._set_espinhos

    def topo_do_chao(self, x, y_inicial=None):
        """Y da superfície sólida mais alta abaixo de y_inicial na coluna de x (ou None se for um buraco)."""
        c = int(x // TILE)
        r = self.linhas - 1 if y_inicial is None else int(y_inicial // TILE)
        while r >= 0:
            if (c, r) in self.grade:
                return (r + 1) * TILE
            r -= 1
        return None

    # ------------------------------------------------------------ montagem dos sprites
    def construir(self):
        """Retorna (blocos, espinhos, decoracao) como arcade.SpriteList."""
        blocos = arcade.SpriteList(use_spatial_hash=True)
        for (c, r), tipo in self.grade.items():
            if tipo == "plat":
                t = "plat"
            else:
                t = "topo" if (c, r + 1) not in self.grade else "miolo"
            blocos.append(Bloco(self.tema_tiles, t, c, r))
        esp = arcade.SpriteList()
        for c, r in self.espinhos:
            esp.append(Espinho(c, r))
        deco = arcade.SpriteList()
        for nome, x, y, ancora in self._decoracao_total():
            tex = recursos.textura("deco", nome + ".png")
            s = arcade.Sprite(tex, scale=1.0, center_x=x, center_y=y)
            if ancora == "base":
                s.bottom = y
            elif ancora == "topo":
                s.top = y
            deco.append(s)
        return blocos, esp, deco

    def _decoracao_total(self):
        itens = list(self.decos)
        rng = random.Random(len(self.grade) * 7 + self.colunas)
        c = 6
        while c < self.colunas - 4:
            c += rng.randint(5, 11)
            y = self.topo_do_chao(c * TILE + 16)
            if y is None or (c, int(y // TILE) - 1) not in self.grade:
                continue
            if self.grade.get((c, int(y // TILE) - 1)) == "plat":
                continue
            if self.tema_fundo == "cem":
                nome = rng.choice(["lapide", "lapide", "cruz", "arvore", "cerca"])
                itens.append((nome, c * TILE + 16, y, "base"))
            elif self.tema_fundo == "salao":
                if rng.random() < 0.45:
                    itens.append(("pilar", c * TILE + 16, y, "base"))
                elif rng.random() < 0.5:
                    itens.append(("estandarte", c * TILE + 16, 17 * TILE, "topo"))
                else:
                    itens.append(("janela", c * TILE + 16, y + 150, "base"))
            elif self.tema_fundo == "torre":
                if rng.random() < 0.5:
                    itens.append(("janela_azul", c * TILE + 16, y + 150, "base"))
                else:
                    itens.append(("estandarte", c * TILE + 16, 17 * TILE, "topo"))
            elif self.tema_fundo == "arena":
                if rng.random() < 0.6:
                    itens.append(("pilar", c * TILE + 16, y, "base"))
        if self.tema_fundo in ("salao", "arena"):
            for c in range(10, self.colunas, 17):
                itens.append(("lustre", c * TILE, 18 * TILE, "topo"))
        return itens

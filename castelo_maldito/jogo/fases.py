"""Definição (por código) das quatro fases: Cemitério, Salão, Torre e a arena do chefe."""
from .config import FASES, VEL_CORRIDA_MULT
from .mapa import Mapa


def _novo(i, colunas):
    tiles, fundo, nome, musica = FASES[i]
    return Mapa(tiles, fundo, nome, musica, colunas)


def fase_cemiterio():
    m = _novo(0, 130)
    m.chao(0, 40, 3)
    m.chao(44, 77, 3)
    m.plataforma(79, 5, 2)
    m.chao(85, 130, 3)
    m.massa(30, 3, 2, 1)                 # degrau
    m.massa(60, 3, 3, 1)
    m.espinhos_em(96, 100, 3)
    m.plataforma(98, 5, 3)               # caminho alto
    m.plataforma(102, 7, 6)
    m.largada(3, 3)
    m.checkpoint(60, 4)
    m.checkpoint(105, 3)
    m.porta_em(124, 3)
    for c, d in ((8, "coracao"), (18, "adaga"), (34, "coracao"), (50, "carne"), (66, "coracao_g"),
                 (88, "coracao"), (92, "moeda"), (118, "bolsa")):
        m.vela(c, 3, d)
    m.vela(107, 8, "cruz")
    m.item("arma1", 104, 8)
    for c0, c1 in ((12, 40), (44, 76), (100, 122)):
        m.zona("zumbi", c0, c1)
    for c in (56, 70, 108):
        m.inimigo("esqueleto", c, 3)
    m.inimigo("esqueleto", 90, 3)
    for c, r in ((50, 12), (76, 12), (90, 11), (112, 12)):
        m.inimigo("morcego", c, r)
    return m


def fase_salao():
    m = _novo(1, 140)
    m.chao(0, 60, 3)
    m.chao(64, 100, 3)
    m.chao(112, 140, 3)
    m.massa(0, 15, 140, 3)               # teto
    m.massa(30, 3, 6, 2)                 # bloco elevado
    m.plataforma(37, 4, 2)
    m.plataforma(40, 6, 10)              # galeria
    m.plataforma(102, 5, 2)
    m.plataforma(106, 6, 2)
    m.espinhos_em(66, 70, 3)
    m.espinhos_em(84, 87, 3)
    m.largada(3, 3)
    m.checkpoint(55, 3)
    m.checkpoint(95, 3)
    m.porta_em(134, 3)
    for c, r, d in ((10, 3, "coracao"), (26, 3, "machado"), (45, 7, "agua"), (62, 3, None),
                    (76, 3, "coracao_g"), (90, 3, "carne"), (120, 3, "coracao"), (127, 3, "bumerangue")):
        m.vela(c, r, d)
    m.vela(108, 7, "cruz")
    m.item("arma2", 48, 7)
    for c, r in ((22, 3), (48, 3), (80, 3), (120, 3)):
        m.inimigo("cavaleiro", c, r)
    for c, r in ((14, 3), (70, 3), (90, 3), (44, 7), (128, 3)):
        m.inimigo("esqueleto", c, r)
    for c in (20, 52, 74, 118):
        m.inimigo("morcego", c, 13)
    m.inimigo("fantasma", 75, 5)
    m.inimigo("fantasma", 105, 6)
    for c in range(8, 136, 14):
        m.tocha(c, 7)
    return m


def fase_torre():
    m = _novo(2, 140)
    m.chao(0, 16, 3)
    m.chao(20, 34, 3)
    m.chao(34, 38, 4)
    m.chao(38, 42, 5)
    m.chao(42, 46, 6)
    m.plataforma(48, 7, 3)
    m.plataforma(53, 8, 3)
    m.plataforma(58, 9, 3)
    m.chao(63, 80, 4)
    m.chao(84, 100, 4)
    m.espinhos_em(88, 92, 4)
    m.plataforma(101, 6, 2)
    m.chao(105, 140, 4)
    m.plataforma(109, 5, 2)
    m.plataforma(112, 7, 6)
    m.largada(3, 3)
    m.checkpoint(66, 4)
    m.checkpoint(108, 4)
    m.porta_em(134, 4)
    for c, r, d in ((9, 3, "coracao"), (28, 3, "agua"), (40, 5, "coracao"), (72, 4, "coracao_g"),
                    (96, 4, "carne"), (122, 4, "coracao"), (130, 4, "calice")):
        m.vela(c, r, d)
    m.vela(115, 8, "cruz")
    m.item("arma3", 114, 8)
    m.zona("medusa", 20, 34)
    m.zona("medusa", 63, 99)
    for c, r in ((70, 4), (93, 4), (118, 4), (128, 4)):
        m.inimigo("cavaleiro", c, r)
    for c, r in ((26, 3), (36, 4), (76, 4), (110, 4), (124, 4)):
        m.inimigo("esqueleto", c, r)
    for c, r in ((14, 5), (115, 7), (125, 6)):
        m.inimigo("fantasma", c, r)
    for c in (30, 66, 98):
        m.inimigo("morcego", c, 12)
    for c in range(6, 136, 12):
        m.tocha(c, 7)
    return m


def fase_arena():
    m = _novo(3, 32)
    m.chao(0, 32, 2)
    m.massa(0, 2, 1, 16)
    m.massa(31, 2, 1, 16)
    m.plataforma(4, 5, 4)
    m.plataforma(24, 5, 4)
    m.plataforma(14, 8, 4)
    m.largada(3, 2)
    m.chefe = (16, 2)
    for c, d in ((7, "carne"), (25, "carne"), (11, "coracao_g"), (21, "coracao_g")):
        m.vela(c, 2, d)
    for c in (5, 12, 19, 26):
        m.tocha(c, 6)
    return m


class _Trilha:
    """Pequena 'linguagem' para montar o percurso da corrida da esquerda para a direita.

    c = coluna atual, h = altura do chão (em tiles). Cada trecho avança c. Limites que o Dodo (e o jogador) vencem:
    vão até 5 tiles no plano, 4 subindo 1, 3 subindo 2, 2 subindo 3; muros de até 3 tiles; espinhos de até 4 tiles.
    """

    def __init__(self, m, c=0, h=3):
        self.m, self.c, self.h = m, c, h

    def plano(self, n):
        self.m.chao(self.c, self.c + n, self.h)
        self.c += n
        return self

    def vao(self, v, n, dh=0):
        """Buraco de v tiles e depois n tiles de chão (dh = diferença de altura do chão novo)."""
        self.c += v
        self.h += dh
        return self.plano(n)

    def sobe(self, dh, n):
        """Degrau para cima (sem buraco)."""
        self.h += dh
        return self.plano(n)

    def desce(self, dh, n):
        self.h -= dh
        return self.plano(n)

    def espinhos(self, k, antes=3, depois=3):
        """Chão com k tiles de espinhos no meio (é preciso pular)."""
        self.plano(antes)
        self.m.chao(self.c, self.c + k, self.h)
        self.m.espinhos_em(self.c, self.c + k, self.h)
        self.c += k
        return self.plano(depois)

    def muro(self, alt, antes=4, depois=4):
        """Parede estreita de alt tiles de altura no meio do chão (é preciso pular)."""
        self.plano(antes + 1 + depois)
        self.m.massa(self.c - depois - 1, self.h, 1, alt)
        return self

    def ponte(self, k, w, v):
        """k plataformas finas de w tiles, separadas por vãos de v tiles, na altura do chão atual."""
        for i in range(k):
            self.m.plataforma(self.c, self.h - 1, w)
            self.c += w + (v if i < k - 1 else 0)
        return self


def fase_corrida():
    """Corrida contra o Dodo: percurso longo de pulos; o Dodo faz o mesmo caminho. Cenário do Salão (fase 2)."""
    m = _novo(4, 1)
    m.mult_vel = VEL_CORRIDA_MULT
    t = _Trilha(m, 0, 3)
    t.plano(16)                                                    # largada
    # ---- ato 1: aquecimento (vãos simples e degraus)
    t.vao(3, 8).vao(3, 6).vao(4, 8)
    t.sobe(1, 6).sobe(1, 6).desce(2, 6)
    t.vao(4, 5).vao(4, 6).vao(5, 7)
    # ---- ato 2: pontes de plataformas finas, espinhos e muros
    t.ponte(4, 3, 3).plano(6)
    t.espinhos(3).muro(2).espinhos(4)
    t.vao(3, 5, dh=1).vao(3, 5, dh=1).vao(3, 4, dh=1)
    t.desce(3, 6).muro(3)
    t.vao(5, 6)
    # ---- ato 3: escadaria, ilhas altas e baixas
    t.sobe(1, 4).sobe(1, 4).sobe(1, 4).vao(3, 5, dh=1).desce(1, 4).desce(1, 4).desce(1, 4)
    t.vao(3, 4, dh=2).vao(3, 4, dh=-2).vao(3, 4, dh=2).vao(3, 4, dh=-2)
    t.ponte(5, 3, 4).plano(5)
    t.espinhos(4).vao(5, 6).espinhos(3, 2, 2).muro(3)
    # ---- ato 4: sprint final (tudo misturado)
    t.muro(2, 3, 3).muro(3, 3, 3).espinhos(3, 3, 2).vao(5, 5)
    t.ponte(4, 3, 4).plano(4).vao(3, 4, dh=1).vao(3, 4, dh=1).desce(2, 5)
    t.espinhos(4).vao(5, 5).muro(3)
    fim = t.c + 2                                                  # linha de chegada
    t.plano(14)                                                    # chão depois da chegada
    m.colunas = t.c
    m.largada(3, 3)
    m.corrida = dict(fim=fim, dodo=(6, 3))
    for c in range(8, m.colunas - 4, 14):
        m.tocha(c, 7)
    return m


_FABRICAS = [fase_cemiterio, fase_salao, fase_torre, fase_arena, fase_corrida]


def construir_fase(indice):
    return _FABRICAS[indice]()

"""Conde Vorthal, o chefe final.

Etapa 1: luta normal em três fases de ataques (bolas de fogo, teleporte + garra, pilares, ondas).
Etapa 2: ao zerar a vida ele não morre: fica parado no alto, invulnerável, e o jogador só precisa SOBREVIVER ao
roteiro (gafanhotos, inimigos invocados, cruz de fogo). Se sobreviver, tudo morre junto com ele.
"""
import math
import random

from . import recursos
from .config import DIREITA, ESQUERDA, TILE
from .corpo import sinal
from .inimigos import FABRICA, Inimigo
from .invocacoes import CruzFogo, Gafanhoto
from .projeteis import BolaFogo, Onda, Pilar

IDLE0, IDLE1, CAST, GOLPE, RUGIDO = range(5)


class Chefe(Inimigo):
    chave = "sprites/chefe"
    hp = 80
    dano_contato = 4
    pontos = 5000
    nome = "Conde Vorthal"

    CARGA_BOLAS = 0.95   # s entre começar a piscar em vermelho e soltar o fogo (antes eram 0.6 s, sem aviso)
    CHANCE_TELEPORTE = {1: 0.45, 2: 0.6, 3: 0.75}   # chance de reaparecer em outro ponto antes de um ataque

    # Roteiro da etapa 2: (ataque, duração em s, nível de intensidade 0-2). Os ataques se repetem em 3 rodadas.
    # A soma das durações é o tempo que o jogador precisa sobreviver (barra "SOBREVIVA!" no HUD).
    ROTEIRO_F2 = [
        ("gafanhotos", 4.0, 0), ("pausa", 1.5, 0), ("invocar", 3.2, 0), ("pausa", 1.5, 0), ("cruz", 4.2, 0), ("pausa", 1.5, 0),
        ("cruz", 4.2, 1), ("pausa", 1.2, 1), ("gafanhotos", 4.4, 1), ("pausa", 1.2, 1), ("invocar", 3.4, 1), ("pausa", 1.2, 1),
        ("gafanhotos", 4.6, 2), ("pausa", 1.0, 2), ("cruz", 4.2, 2), ("pausa", 1.0, 2), ("invocar", 3.6, 2),
        ("pausa", 1.0, 2), ("gafanhotos", 4.6, 2), ("pausa", 3.0, 2),
    ]
    FAIXAS_GAFANHOTO = (30, 70, 110, 160, 215, 270)   # alturas (acima do chão) por onde o enxame passa
    INVOCACAO = [   # quem aparece em cada nível (máx. 8 inimigos vivos ao mesmo tempo)
        ("esqueleto", "esqueleto", "morcego", "morcego"),
        ("esqueleto", "esqueleto", "esqueleto", "morcego", "morcego", "fantasma"),
        ("esqueleto", "esqueleto", "cavaleiro", "morcego", "morcego", "morcego", "fantasma"),
    ]

    def __init__(self, x, y_pes, etapa=1):
        super().__init__(x, y_pes)
        self.meia_l = 34
        self.meia_a = 66
        self.center_y = y_pes + self.meia_a + 1
        self.estado = "intro"
        self.t = 0.0
        self.espera = 1.0
        self.disparou = False
        self.proximo = "idle"
        self.destino_x = x
        self.ultimo = None
        self.virado = ESQUERDA
        self.explosoes = 0.0
        self.y_piso = y_pes      # chão da arena (de onde saem pilares e ondas)
        self.pe_y = y_pes        # altura atual dos pés (muda ao teleportar para uma plataforma)
        self.destino = None      # (x, y_pes) do próximo teleporte
        self.plats = None        # [(x_centro, y_topo)] das plataformas da arena
        self.marcas = 0
        self.avisou = False
        # etapa 2 (sobreviver)
        self.etapa = etapa
        self.passo = 0
        self.passo_t = 0.0
        self.f2_t = 0.0
        self.f2_flags = set()
        self.f2_plano = []
        self.f2_n = 0
        self.f2_lado = random.choice((DIREITA, ESQUERDA))
        self.f2_total = sum(d for _, d, _ in self.ROTEIRO_F2)
        if etapa == 2:               # renascer depois de já ter vencido a etapa 1: recomeça só a sobrevivência
            self.hp_atual = 0
            self.estado = "f2_intro"

    @property
    def progresso_f2(self):
        return min(1.0, self.f2_t / self.f2_total)

    @property
    def restante_f2(self):
        return max(0.0, self.f2_total - self.f2_t)

    @property
    def sem_contato(self):
        """Sem dano por encostar nele (surgindo/sumindo, morrendo ou na etapa 2)."""
        return self.etapa == 2 or self.estado in ("sumir", "aparecer", "morrendo", "intro", "transicao")

    @property
    def fase(self):
        f = self.hp_atual / self.hp
        return 1 if f > 0.66 else (2 if f > 0.33 else 3)

    @property
    def caixa_golpe(self):
        if self.estado == "golpe" and self.t >= 0.45:
            x = self.center_x
            if self.virado == DIREITA:
                return (x, self.center_y - 60, x + 110, self.center_y + 30)
            return (x - 110, self.center_y - 60, x, self.center_y + 30)
        return None

    def receber_dano(self, dano, origem_x, empurrao=0):
        if self.etapa == 2 or self.estado in ("morrendo", "intro", "transicao"):
            return "bloqueado"
        self.hp_atual -= dano
        self.flash = 0.1
        self.color = (255, 130, 130, 255)
        if self.hp_atual <= 0:
            # vida zerada: ele não morre, entra na etapa 2 (o jogador precisa sobreviver)
            self.hp_atual = 0
            self.estado = "transicao"
            self.t = 0.0
            self.alpha = 255
            self.disparou = False
            self.explosoes = 0.0
        return "ferido"

    # ------------------------------------------------------------------ escolha de ataque
    def _escolher(self, jogo):
        opcoes = ["bolas", "garra"]
        if self.fase >= 2:
            opcoes += ["pilares", "onda"]
        if self.fase >= 3:
            opcoes += ["bolas", "pilares"]
        if self.ultimo in opcoes and len(opcoes) > 1:
            opcoes.remove(self.ultimo)
        escolha = random.choice(opcoes)
        self.ultimo = escolha
        self.t = 0.0
        self.disparou = False
        self.avisou = False
        self.marcas = 0
        self.virar_para(jogo.jogador.center_x)
        destino = None
        if escolha == "garra":
            destino = self._destino_garra(jogo)
        elif random.random() < self.CHANCE_TELEPORTE[self.fase]:
            destino = self._destino_livre(jogo)      # reaparece em outro ponto (chão ou plataforma) e ataca de lá
        if destino:
            self.destino = destino
            self.estado, self.proximo = "sumir", ("golpe" if escolha == "garra" else escolha)
            jogo.audio.tocar("teleporte")
        else:
            self.estado = escolha

    # ------------------------------------------------------------------ teleporte
    def _plataformas(self, mapa):
        """(x_centro, y_topo) de cada plataforma suspensa: trechos contínuos de tiles 'plat' na mesma linha."""
        linhas = {}
        for (c, r), tipo in mapa.grade.items():
            if tipo == "plat":
                linhas.setdefault(r, []).append(c)
        res = []
        for r, cols in linhas.items():
            cols.sort()
            ini = ant = cols[0]
            for c in cols[1:] + [None]:
                if c is not None and c == ant + 1:
                    ant = c
                    continue
                res.append(((ini + ant + 1) * TILE / 2, (r + 1) * TILE))
                if c is not None:
                    ini = ant = c
        return res

    def _tem_apoio(self, mapa, x, nivel, y_ref):
        """True se há chão/plataforma na altura 'nivel' sob o corpo do chefe centrado em x."""
        for dx in (-28, 0, 28):
            topo = mapa.topo_do_chao(x + dx, y_ref)
            if topo is not None and abs(topo - nivel) < 1:
                return True
        return False

    def _cabe(self, mapa, x, y_pe):
        """True se o corpo inteiro do chefe (132 px de altura) cabe em (x, y_pe) sem entrar em blocos."""
        return not mapa.colide(x - self.meia_l, y_pe + 1, x + self.meia_l, y_pe + 2 * self.meia_a)

    def _chao_livre_perto(self, mapa, x0):
        """Ponto do chão mais próximo de x0 onde o chefe cabe (as plataformas baixas ficam a 96 px do chão)."""
        lim0, lim1 = 3 * TILE, mapa.largura_px - 3 * TILE
        for off in (0, 100, -100, 200, -200, 300, -300):
            x = max(lim0, min(lim1, x0 + off))
            if self._cabe(mapa, x, self.y_piso):
                return x
        return None

    def _destino_garra(self, jogo):
        """Garra: reaparece colado no jogador, no mesmo nível dele (chão ou a plataforma onde ele está)."""
        p, m = jogo.jogador, jogo.mapa
        lim0, lim1 = 3 * TILE, m.largura_px - 3 * TILE
        nivel = m.topo_do_chao(p.center_x, p.center_y)
        if nivel is None:
            nivel = self.y_piso
        dist = 120 if nivel <= self.y_piso + 1 else 75
        lados = [-1, 1]
        random.shuffle(lados)
        for lado in lados:
            x = p.center_x + lado * dist
            if lim0 <= x <= lim1 and self._tem_apoio(m, x, nivel, p.center_y) and self._cabe(m, x, nivel):
                return x, nivel
        x = self._chao_livre_perto(m, p.center_x + lados[0] * 120)   # sem apoio perto: desce para o chão
        if x is None:
            x = self.center_x
        return x, self.y_piso

    def _destino_livre(self, jogo):
        """Outro ponto da arena: plataformas (dá para bater nele pulando) ou chão, longe do jogador e do ponto atual."""
        p, m = jogo.jogador, jogo.mapa
        lim0, lim1 = 3 * TILE, m.largura_px - 3 * TILE
        pe_jog = p.center_y - p.meia_a

        def valido(x, y):
            if not self._cabe(m, x, y):                                       # o corpo dele não cabe ali
                return False
            if abs(x - self.center_x) < 70 and abs(y - self.pe_y) < 10:     # é onde ele já está
                return False
            if abs(x - p.center_x) < 100 and abs(y - pe_jog) < 150:         # em cima do jogador
                return False
            return True

        plats = [(x, y) for x, y in self.plats if valido(x, y)]
        chao = None
        for _ in range(8):
            x = random.uniform(lim0, lim1)
            if valido(x, self.y_piso):
                chao = (x, self.y_piso)
                break
        if plats and (chao is None or random.random() < 0.65):
            return random.choice(plats)
        return chao

    def _reduzir_espera(self):
        return {1: 1.3, 2: 1.0, 3: 0.7}[self.fase]

    def ia(self, dt, jogo):
        self.passo_comum(dt)
        self.mapa = jogo.mapa
        if self.plats is None:
            self.plats = self._plataformas(jogo.mapa)
        if self.etapa == 1 or self.estado == "morrendo":
            self.cair(jogo)
        p = jogo.jogador
        self.t += dt
        e = self.estado
        y_chao = self.y_piso
        if e.startswith("f2"):
            self._ia_fase2(dt, jogo)
            return
        if e == "intro":
            self.definir_quadro(RUGIDO)
            if self.t < 0.1 and self.alpha == 255 and not self.disparou:
                self.disparou = True
                jogo.audio.tocar("rugido")
                jogo.tremer(1.0)
            if self.t >= 1.8:
                self.estado, self.t, self.espera = "idle", 0.0, 0.8
        elif e == "idle":
            self.virar_para(p.center_x)
            self.definir_quadro(IDLE0 if int(self.tempo * 3) % 2 == 0 else IDLE1)
            self.espera -= dt
            if self.espera <= 0:
                self._escolher(jogo)
        elif e == "bolas":
            self.definir_quadro(CAST)
            if self.t >= 0.15 and not self.disparou:       # aviso: pisca em vermelho até soltar o fogo
                if not self.avisou:
                    self.avisou = True
                    jogo.audio.tocar("pilar_aviso", 0.8)
                if self.flash <= 0:
                    self.color = (255, 60, 60, 255) if int(self.t * 12) % 2 == 0 else (255, 255, 255, 255)
            if self.t >= self.CARGA_BOLAS and not self.disparou:
                self.disparou = True
                if self.flash <= 0:
                    self.color = (255, 255, 255, 255)
                jogo.audio.tocar("bola_fogo")
                n = {1: 1, 2: 3, 3: 5}[self.fase]
                ox = self.center_x + 40 * (1 if self.virado == DIREITA else -1)
                oy = self.center_y + 20
                ang0 = math.atan2(p.center_y - oy, p.center_x - ox)
                for k in range(n):
                    ang = ang0 + (k - (n - 1) / 2) * 0.28
                    jogo.projeteis_inimigos.append(BolaFogo(ox, oy, math.cos(ang) * 5.2, math.sin(ang) * 5.2))
            if self.t >= self.CARGA_BOLAS + 0.5:
                self._voltar_idle()
        elif e == "sumir":
            self.alpha = max(0, int(255 * (1 - self.t / 0.35)))
            dx_, dy_ = self.destino
            # faíscas roxas no ponto de chegada (avisam onde ele vai reaparecer)
            if self.marcas == 0 and self.t >= 0.1:
                self.marcas = 1
                jogo.efeitos.faiscas(dx_, dy_ + 60, (180, 110, 255, 255), 16, 3.0, 0.5, 0.05)
            elif self.marcas == 1 and self.t >= 0.35:
                self.marcas = 2
                jogo.efeitos.faiscas(dx_, dy_ + 60, (220, 170, 255, 255), 12, 4.0, 0.4, 0.05)
            if self.t >= 0.6:
                self.center_x = dx_
                self.pe_y = dy_
                self.center_y = dy_ + self.meia_a + 1
                self.vy = 0.0
                self.virar_para(p.center_x)
                self.estado, self.t = "aparecer", 0.0
        elif e == "aparecer":
            self.alpha = min(255, int(255 * self.t / 0.3))
            if self.t >= 0.3:
                self.alpha = 255
                self.estado, self.t = self.proximo, 0.0
        elif e == "golpe":
            self.definir_quadro(CAST if self.t < 0.45 else GOLPE)
            if abs(self.t - 0.45) < dt:
                jogo.audio.tocar("golpe_pesado")
            if self.t >= 0.75:
                self._voltar_idle()
        elif e == "pilares":
            self.definir_quadro(RUGIDO)
            if self.t >= 0.4 and not self.disparou:
                self.disparou = True
                jogo.audio.tocar("pilar_aviso")
                n = {1: 2, 2: 3, 3: 4}[self.fase]
                xs = [p.center_x] + [random.uniform(3 * TILE, jogo.mapa.largura_px - 3 * TILE) for _ in range(n - 1)]
                for x in xs:
                    jogo.projeteis_inimigos.append(Pilar(x, y_chao))
            if self.t >= 1.2:
                self._voltar_idle()
        elif e == "onda":
            self.definir_quadro(GOLPE if self.t >= 0.4 else CAST)
            if self.t >= 0.4 and not self.disparou:
                self.disparou = True
                jogo.audio.tocar("fogo")
                s = DIREITA if self.virado == DIREITA else ESQUERDA
                jogo.projeteis_inimigos.append(Onda(self.center_x + 50 * sinal(1 if s == DIREITA else -1),
                                                    y_chao + 20, s))
            if self.t >= 0.9:
                self._voltar_idle()
        elif e == "transicao":
            self.definir_quadro(RUGIDO)
            if not self.disparou:
                self.disparou = True
                jogo.fase2 = True                       # se o jogador morrer daqui em diante, recomeça na etapa 2
                jogo.projeteis_inimigos.clear()
                jogo.perigos.clear()
                for o in list(jogo.inimigos):
                    if o is not self:
                        o.remove_from_sprite_lists()
                jogo.audio.tocar("rugido")
                jogo.tremer(1.2)
            self.explosoes -= dt
            if self.explosoes <= 0:
                self.explosoes = 0.16
                jogo.explodir(self.center_x + random.uniform(-50, 50), self.center_y + random.uniform(-60, 60))
            self.alpha = 255 if int(self.t * 12) % 2 else 160
            if self.t >= 2.2:
                self._iniciar_fase2(jogo)
        elif e == "morrendo":
            self.definir_quadro(RUGIDO)
            self.explosoes -= dt
            if self.explosoes <= 0:
                self.explosoes = 0.18
                jogo.explodir(self.center_x + random.uniform(-50, 50), self.center_y + random.uniform(-60, 60))
            self.alpha = 255 if int(self.t * 12) % 2 else 160
            if self.t >= 2.6:
                self.morreu = True

    # ------------------------------------------------------------------ etapa 2: sobreviver
    def _iniciar_fase2(self, jogo):
        self.etapa = 2
        self.alpha = 255
        self.color = (255, 255, 255, 255)
        self.estado, self.t = "f2_intro", 0.0
        self.disparou = False
        self.passo, self.passo_t, self.f2_t = 0, 0.0, 0.0
        self.f2_flags = set()
        jogo._recriar_velas()          # os castiçais voltam para dar corações e vida antes da sobrevivência

    def _ia_fase2(self, dt, jogo):
        p = jogo.jogador
        self.virar_para(p.center_x)
        self.center_x = jogo.mapa.largura_px / 2          # parado no alto, no centro (só flutua de leve)
        self.center_y = self.y_piso + self.meia_a + 270 + math.sin(self.tempo * 2.0) * 6
        self.alpha = 255
        if self.estado == "f2_intro":
            self.definir_quadro(RUGIDO)
            if not self.disparou:
                self.disparou = True
                jogo.audio.tocar("rugido")
                jogo.tremer(0.6)
                jogo.avisar("SOBREVIVA!")
            if self.t >= 2.2:
                self.estado, self.t = "f2_roteiro", 0.0
                self.passo, self.passo_t, self.f2_t = 0, 0.0, 0.0
                self.f2_flags = set()
            return
        if self.passo >= len(self.ROTEIRO_F2):
            self._f2_vitoria(jogo)
            return
        acao, dur, nivel = self.ROTEIRO_F2[self.passo]
        self.passo_t += dt
        self.f2_t += dt
        getattr(self, "_f2_" + acao)(dt, jogo, nivel)
        if self.passo_t >= dur:
            self.passo += 1
            self.passo_t = 0.0
            self.f2_flags = set()

    def _f2_pausa(self, dt, jogo, nivel):
        self.definir_quadro(IDLE0 if int(self.tempo * 3) % 2 == 0 else IDLE1)

    def _f2_gafanhotos(self, dt, jogo, nivel):
        """Onda de gafanhotos atravessando a arena (alterna o lado de entrada a cada vez)."""
        n = (9, 12, 15)[nivel]
        vel = (4.2, 5.0, 5.8)[nivel]
        espaco = 0.12
        self.definir_quadro(CAST)
        larg = jogo.mapa.largura_px
        if "lado" not in self.f2_flags:
            self.f2_flags.add("lado")
            self.f2_lado = DIREITA if self.f2_lado == ESQUERDA else ESQUERDA
            self.f2_n = 0
            jogo.audio.tocar("pilar_aviso", 0.8)
        entra_esq = self.f2_lado == DIREITA
        if self.passo_t < 0.9 and int(self.passo_t * 20) != int((self.passo_t - dt) * 20):
            # aviso: faíscas verdes na borda por onde o enxame vai entrar
            jogo.efeitos.faiscas(50 if entra_esq else larg - 50, self.y_piso + random.uniform(20, 280),
                                 (170, 220, 90, 255), 4, 2.0, 0.4, 0.05)
        if self.passo_t >= 0.9:
            devidos = min(n, int((self.passo_t - 0.9) / espaco) + 1)
            while self.f2_n < devidos:
                y = self.y_piso + random.choice(self.FAIXAS_GAFANHOTO)
                jogo.inimigos.append(Gafanhoto(-20 if entra_esq else larg + 20, y, self.f2_lado, vel))
                self.f2_n += 1

    def _f2_invocar(self, dt, jogo, nivel):
        """Invoca inimigos comuns (com marcas de aviso no ponto onde vão nascer)."""
        self.definir_quadro(RUGIDO)
        p = jogo.jogador
        larg = jogo.mapa.largura_px
        if "plano" not in self.f2_flags:
            self.f2_flags.add("plano")
            vivos = sum(1 for o in jogo.inimigos if o is not self and not isinstance(o, Gafanhoto))
            self.f2_plano = []
            for tipo in self.INVOCACAO[nivel][: max(0, 8 - vivos)]:
                if tipo in ("morcego", "fantasma"):
                    x, y = random.uniform(120, larg - 120), self.y_piso + random.uniform(130, 260)
                else:
                    x = random.uniform(300, larg - 300)
                    for _ in range(10):
                        if abs(x - p.center_x) > 120:
                            break
                        x = random.uniform(300, larg - 300)
                    y = self.y_piso
                self.f2_plano.append((tipo, x, y))
            jogo.audio.tocar("teleporte", 0.8)
        for marca, t0 in (("m1", 0.2), ("m2", 0.6)):
            if self.passo_t >= t0 and marca not in self.f2_flags:
                self.f2_flags.add(marca)
                for _, x, y in self.f2_plano:
                    jogo.efeitos.faiscas(x, y + 24, (180, 110, 255, 255), 10, 3.0, 0.5, 0.05)
        if self.passo_t >= 1.0 and "nasceu" not in self.f2_flags:
            self.f2_flags.add("nasceu")
            for tipo, x, y in self.f2_plano:
                e = FABRICA[tipo](x, y)
                e.mapa = jogo.mapa
                if tipo == "morcego":
                    e.estado = "voando"
                jogo.inimigos.append(e)
                jogo.efeitos.faiscas(x, y + 24, (220, 170, 255, 255), 12, 4.0, 0.4, 0.05)

    def _f2_cruz(self, dt, jogo, nivel):
        """Cruz de fogo no meio da arena: avisa (contorno piscando) e depois queima."""
        self.definir_quadro(CAST if self.passo_t < 1.5 else GOLPE)
        if "cruz" not in self.f2_flags:
            self.f2_flags.add("cruz")
            jogo.perigos.append(CruzFogo(jogo.mapa.largura_px / 2, self.y_piso, nivel))
            jogo.audio.tocar("pilar_aviso")

    def _f2_vitoria(self, jogo):
        """O jogador sobreviveu: tudo que foi invocado morre junto com o chefe."""
        for o in list(jogo.inimigos):
            if o is not self:
                jogo.efeitos.faiscas(o.center_x, o.center_y, (255, 200, 90, 255), 10, 4.0, 0.5, 0.2)
                o.remove_from_sprite_lists()
        jogo.audio.tocar("explosao")
        jogo.perigos.clear()
        jogo._chefe_cai()
        self.estado, self.t = "morrendo", 0.0
        self.explosoes = 0.0

    def _voltar_idle(self):
        if self.flash <= 0:
            self.color = (255, 255, 255, 255)
        self.estado, self.t, self.espera = "idle", 0.0, self._reduzir_espera()

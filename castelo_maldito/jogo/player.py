"""O herói: física de plataforma (PhysicsEnginePlatformer), ataques e máquina de estados de animação."""
import arcade

from . import recursos
from .armas import ESPADAS, SUBARMAS
from .audio import audio
from .config import (DIREITA, ESQUERDA, FORCA_PULO, GRAVIDADE, INVULNERAVEL_APOS_DANO, Q_ANDAR, Q_ATQ_GOLPE,
                     Q_ATQ_PREP, Q_ATQ_RECUP, Q_CAST, Q_DASH, Q_FERIDO, Q_IDLE, Q_MORTO, Q_PULO, Q_QUEDA,
                     RECARGA_DASH, TEMPO_ANIMACAO_CAMINHADA, TEMPO_BUFFER_PULO, TEMPO_COYOTE, TEMPO_DASH,
                     VEL_ANDAR, VEL_DASH, VEL_QUEDA_MAX)

K = arcade.key


class Entrada:
    """Estado do teclado: teclas seguradas + eventos de 'apertou agora' consumidos pelo jogador."""

    PULO = {K.SPACE, K.UP, K.W}
    ATAQUE = {K.Z, K.J}
    SUB = {K.X, K.K}
    DASH = {K.C, K.L, K.LSHIFT}
    ESQ = {K.LEFT, K.A}
    DIR = {K.RIGHT, K.D}

    def __init__(self):
        self.seguradas = set()
        self.eventos = set()

    def pressionar(self, tecla):
        self.seguradas.add(tecla)
        for nome, grupo in (("pulo", self.PULO), ("ataque", self.ATAQUE), ("sub", self.SUB), ("dash", self.DASH)):
            if tecla in grupo:
                self.eventos.add(nome)

    def soltar(self, tecla):
        self.seguradas.discard(tecla)

    def clicar(self, botao):
        """Mouse: botão esquerdo = espada, botão direito = sub-arma."""
        if botao == arcade.MOUSE_BUTTON_LEFT:
            self.eventos.add("ataque")
        elif botao == arcade.MOUSE_BUTTON_RIGHT:
            self.eventos.add("sub")

    def limpar(self):
        self.seguradas.clear()
        self.eventos.clear()

    def algum(self, grupo):
        return bool(self.seguradas & grupo)

    @property
    def esquerda(self):
        return self.algum(self.ESQ)

    @property
    def direita(self):
        return self.algum(self.DIR)

    @property
    def pulo_segurado(self):
        return self.algum(self.PULO)

    def consumir(self, nome):
        if nome in self.eventos:
            self.eventos.discard(nome)
            return True
        return False


def _com_caixa(tex, meia_l=12, meia_a=36):
    """Troca a hit box da textura por um retângulo justo no corpo (a folha tem a espada ocupando espaço)."""
    try:
        pts = ((-meia_l, -meia_a), (meia_l, -meia_a), (meia_l, meia_a), (-meia_l, meia_a))
        return arcade.Texture(tex.image, hit_box_points=pts)
    except Exception:
        return tex


class Player(arcade.Sprite):
    meia_l = 11
    meia_a = 34

    def __init__(self, x, y, progresso, entrada):
        direita, esquerda = recursos.quadros("sprites/player")
        self.texturas = {DIREITA: [_com_caixa(t) for t in direita], ESQUERDA: [_com_caixa(t) for t in esquerda]}
        super().__init__(self.texturas[DIREITA][Q_IDLE], scale=1.0, center_x=x, center_y=y)
        self.prog = progresso
        self.entrada = entrada
        self.fisica = None
        self.jogo = None
        self.virado_para = DIREITA
        self.indice_andar = 0
        self.tempo_quadro = 0.0
        self.no_chao = False
        # temporizadores
        self.coyote = 0.0
        self.buffer_pulo = 0.0
        self.dash_tempo = 0.0
        self.dash_recarga = 0.0
        self.dash_no_ar = False
        self.invul = 0.0
        self.ferido = 0.0
        self.cast_tempo = 0.0
        self.ataque = None
        self.morto = False
        self.tempo_morto = 0.0
        self.acertos_vampiro = 0
        self.mult_vel = 1.0      # fase de corrida: velocidade de andar maior

    # ------------------------------------------------------------------ propriedades
    def vincular_fisica(self, fisica):
        self.fisica = fisica

    @property
    def caixa(self):
        return (self.center_x - self.meia_l, self.center_y - self.meia_a,
                self.center_x + self.meia_l, self.center_y + self.meia_a)

    @property
    def arma(self):
        return ESPADAS[self.prog.arma_atual]

    @property
    def sinal_dir(self):
        return 1 if self.virado_para == DIREITA else -1

    def caixa_ataque(self):
        """Retângulo de dano da espada (somente na fase 'golpe' do ataque)."""
        if not self.ataque or self.ataque["fase"] != "golpe":
            return None
        px = self.center_x + self.sinal_dir * 6
        py = self.center_y + 6
        a = self.arma["alcance"]
        if self.virado_para == DIREITA:
            return (px, py - 50, px + a, py + 50)
        return (px - a, py - 50, px, py + 50)

    def posicao_arco(self):
        """Centro do sprite do arco de golpe (pivô na mão do herói)."""
        px = self.center_x + self.sinal_dir * 6
        return px + self.sinal_dir * 38, self.center_y + 6

    # ------------------------------------------------------------------ ações
    def _pular(self):
        self.change_y = FORCA_PULO
        self.coyote = 0.0
        self.buffer_pulo = 0.0
        audio.tocar("pulo", 0.8)

    def _iniciar_ataque(self):
        self.ataque = {"fase": "prep", "t": 0.0, "acertos": set()}
        audio.tocar(self.arma["som"])

    def _lancar_sub(self):
        sub = self.prog.sub
        if not sub or self.jogo is None:
            return
        custo = SUBARMAS[sub]["custo"]
        if self.prog.coracoes < custo:
            audio.tocar("sem_coracoes")
            return
        self.prog.coracoes -= custo
        self.cast_tempo = 0.22
        self.jogo.lancar_sub(self, sub)

    def receber_dano(self, dano, origem_x):
        """Retorna True se o dano foi aplicado."""
        if self.morto or self.invul > 0 or self.dash_tempo > 0:
            return False
        self.prog.vida = max(0, self.prog.vida - dano)
        audio.tocar("dano")
        self.invul = INVULNERAVEL_APOS_DANO
        self.ferido = 0.28
        self.ataque = None
        self.dash_tempo = 0.0
        lado = 1 if self.center_x >= origem_x else -1
        self.change_x = 5.0 * lado
        self.change_y = 7.0
        if self.jogo:
            self.jogo.tremer(0.2)
        if self.prog.vida <= 0:
            self.morrer()
        return True

    def morrer(self):
        if self.morto:
            return
        self.morto = True
        self.prog.vida = 0
        self.change_x = 0
        self.change_y = max(self.change_y, 6.0)
        self.ataque = None
        self.alpha = 255

    def reviver(self, x, y):
        self.morto = False
        self.tempo_morto = 0.0
        self.center_x, self.center_y = x, y
        self.change_x = self.change_y = 0
        self.invul = 2.0
        self.ferido = 0.0
        self.ataque = None
        self.dash_tempo = 0.0
        self.prog.vida = self.prog.vida_max

    # ------------------------------------------------------------------ atualização
    def update(self, delta_time=1 / 60, *args, **kwargs):
        dt = delta_time
        self._atualizar_temporizadores(dt)
        self.no_chao = bool(self.fisica and self.fisica.can_jump())
        if self.no_chao and self.change_y <= 0:
            self.change_y = 0.0   # no chão a velocidade vertical é zero (base da máquina de estados)
            self.coyote = TEMPO_COYOTE
            self.dash_no_ar = False
        if self.morto:
            self.tempo_morto += dt
            self.change_x = 0
        else:
            self._processar_entrada(dt)
        if self.change_y < -VEL_QUEDA_MAX:
            self.change_y = -VEL_QUEDA_MAX
        self.atualizar_animacao(dt)

    def _atualizar_temporizadores(self, dt):
        self.coyote = max(0.0, self.coyote - dt)
        self.buffer_pulo = max(0.0, self.buffer_pulo - dt)
        self.dash_recarga = max(0.0, self.dash_recarga - dt)
        self.invul = max(0.0, self.invul - dt)
        self.ferido = max(0.0, self.ferido - dt)
        self.cast_tempo = max(0.0, self.cast_tempo - dt)
        self.dash_tempo = max(0.0, self.dash_tempo - dt)
        if self.ataque:
            a = self.ataque
            a["t"] += dt
            arma = self.arma
            if a["fase"] == "prep" and a["t"] >= arma["prep"]:
                a["fase"], a["t"] = "golpe", 0.0
            elif a["fase"] == "golpe" and a["t"] >= arma["golpe"]:
                a["fase"], a["t"] = "recup", 0.0
            elif a["fase"] == "recup" and a["t"] >= arma["recup"]:
                self.ataque = None
        if self.invul > 0 and not self.morto:
            self.alpha = 90 if int(self.invul * 16) % 2 else 255
        else:
            self.alpha = 255

    def _processar_entrada(self, dt):
        e = self.entrada
        if e.consumir("pulo"):
            self.buffer_pulo = TEMPO_BUFFER_PULO
        quer_ataque = e.consumir("ataque")
        quer_sub = e.consumir("sub")
        quer_dash = e.consumir("dash")

        if self.ferido > 0:           # sem controle durante o tranco
            self.change_x *= 0.94
            return

        direcao = (1 if e.direita else 0) - (1 if e.esquerda else 0)

        # dash (impulso horizontal; "congela" a gravidade durante a investida)
        if (quer_dash and self.dash_recarga <= 0 and self.dash_tempo <= 0 and not self.ataque
                and (self.no_chao or not self.dash_no_ar)):
            self.dash_tempo = TEMPO_DASH
            self.dash_recarga = RECARGA_DASH
            self.dash_no_ar = not self.no_chao
            if direcao:
                self.virado_para = DIREITA if direcao > 0 else ESQUERDA
            audio.tocar("dash")
        if self.dash_tempo > 0:
            self.change_x = VEL_DASH * self.sinal_dir
            self.change_y = GRAVIDADE      # a gravidade do motor (-GRAVIDADE) zera a queda neste frame
            return

        # movimento horizontal
        fator = 0.35 if self.ataque else 1.0
        self.change_x = direcao * VEL_ANDAR * fator * self.mult_vel
        if direcao and not self.ataque:
            self.virado_para = DIREITA if direcao > 0 else ESQUERDA

        # pulo: só com apoio (can_jump) ou coyote => sem pulo duplo no ar
        if self.buffer_pulo > 0 and (self.no_chao or self.coyote > 0):
            self._pular()
        if not e.pulo_segurado and self.change_y > 4.0:
            self.change_y *= 0.55          # pulo variável: soltar cedo = pulo curto

        if quer_ataque and not self.ataque:
            self._iniciar_ataque()
        elif quer_sub and not self.ataque and self.cast_tempo <= 0:
            self._lancar_sub()

    # ------------------------------------------------------------------ máquina de estados da animação
    def atualizar_animacao(self, delta_time):
        quadros = self.texturas[self.virado_para]
        # estados especiais (sobrepõem o movimento)
        if self.morto:
            idx = Q_MORTO
        elif self.ferido > 0:
            idx = Q_FERIDO
        elif self.dash_tempo > 0:
            idx = Q_DASH
        elif self.ataque:
            idx = {"prep": Q_ATQ_PREP, "golpe": Q_ATQ_GOLPE, "recup": Q_ATQ_RECUP}[self.ataque["fase"]]
        elif self.cast_tempo > 0:
            idx = Q_CAST
        # estados de movimento, em ordem de prioridade: 1) Pulo/Queda  2) Parado  3) Andando
        elif self.change_y != 0:
            idx = Q_PULO if self.change_y > 0 else Q_QUEDA
        elif self.change_x == 0:
            self.indice_andar = 0
            self.tempo_quadro = 0.0
            idx = Q_IDLE
        else:
            self.tempo_quadro += delta_time
            if self.tempo_quadro >= TEMPO_ANIMACAO_CAMINHADA:
                self.tempo_quadro -= TEMPO_ANIMACAO_CAMINHADA
                self.indice_andar = (self.indice_andar + 1) % len(Q_ANDAR)
            idx = Q_ANDAR[self.indice_andar]
        self.texture = quadros[idx]

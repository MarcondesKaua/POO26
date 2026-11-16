"""Tela inicial: menu principal com atalho [R] para o ranking."""
import arcade

from . import recursos, ui
from .audio import audio
from .config import ALTURA, BRANCO, CINZA, LARGURA, OURO
from .estado import Progresso
from .tela_debug import atalho_debug

K = arcade.key

OPCOES = ["JOGAR", "RANKING  [R]", "CONTROLES", "SAIR"]

CONTROLES = [
    ("← → / A D", "andar"),
    ("ESPAÇO / ↑ / W", "pular (segure = pulo alto; sem pulo duplo)"),
    ("Z / J  ou  MOUSE ESQUERDO", "atacar com a espada"),
    ("X / K  ou  MOUSE DIREITO", "sub-arma (gasta corações)"),
    ("C / L / SHIFT", "dash (esquiva com invulnerabilidade)"),
    ("E / Q  ou  1-4", "trocar de espada"),
    ("F", "trocar de sub-arma (alterna entre os 2 slots)"),
    ("P / ESC", "pausar"),
    ("M", "ligar/desligar o som"),
]

SUBARMAS_AJUDA = [
    "Você carrega até 2 sub-armas. Com um slot livre, a que você pega fica guardada e na mão.",
    "Com os 2 slots cheios, pegar uma nova troca pela que está na sua mão.",
    "A que estava na mão cai no chão: pegue de volta se quiser trocar de novo.",
    "Ela some quando sai da tela. Use [F] para alternar entre as duas guardadas.",
]


class TelaInicial(arcade.View):
    def __init__(self):
        super().__init__()
        self.sel = 0
        self.mostrar_controles = False
        self.t = 0.0

    def on_show_view(self):
        self.window.background_color = (0, 0, 0, 255)
        audio.musica("musica_menu")

    def on_update(self, dt):
        self.t += dt

    def on_draw(self):
        self.clear()
        ui.camera_padrao()
        ui.textura(recursos.textura("bg", "titulo.png"), LARGURA / 2, ALTURA / 2, LARGURA, ALTURA)
        ui.textura(recursos.textura("ui", "logo.png"), LARGURA / 2, ALTURA - 150, 600, 200)
        if self.mostrar_controles:
            ui.retangulo(60, 24, 904, 528, (8, 4, 16, 235))
            ui.contorno(60, 24, 904, 528, OURO, 2)
            ui.texto_sombra("CONTROLES", LARGURA / 2, 515, OURO, 22, "center")
            for i, (tecla, desc) in enumerate(CONTROLES):
                y = 478 - i * 26
                ui.texto(tecla, 100, y, OURO, 15)
                ui.texto(desc, 430, y, BRANCO, 15)
            y0 = 478 - len(CONTROLES) * 26 - 14
            ui.texto_sombra("SUB-ARMAS (2 SLOTS)", LARGURA / 2, y0, OURO, 17, "center")
            for i, linha in enumerate(SUBARMAS_AJUDA):
                ui.texto(linha, 100, y0 - 28 - i * 24, BRANCO, 14)
            ui.texto("[qualquer tecla] voltar", LARGURA / 2, 40, CINZA, 13, "center")
        else:
            for i, op in enumerate(OPCOES):
                y = 300 - i * 48
                ativo = i == self.sel
                cor = OURO if ativo else CINZA
                if ativo:
                    pulso = 4 * abs(((self.t * 2) % 2) - 1)
                    ui.texto_sombra(">", LARGURA / 2 - 120 - pulso, y, OURO, 26, "center")
                ui.texto_sombra(op, LARGURA / 2, y, cor, 26, "center")
            ui.texto("↑ ↓ navegar    ENTER selecionar    [R] ranking", LARGURA / 2, 30, CINZA, 13, "center")

    def on_key_press(self, tecla, mods):
        if atalho_debug(self, tecla, mods):     # Alt+L: menu de testes
            return
        if self.mostrar_controles:
            self.mostrar_controles = False
            return
        if tecla in (K.UP, K.W):
            self.sel = (self.sel - 1) % len(OPCOES)
            audio.tocar("menu_move")
        elif tecla in (K.DOWN, K.S):
            self.sel = (self.sel + 1) % len(OPCOES)
            audio.tocar("menu_move")
        elif tecla == K.R:
            self._ranking()
        elif tecla == K.M:
            audio.alternar_mudo()
        elif tecla in (K.ENTER, K.RETURN, K.SPACE):
            audio.tocar("menu_ok")
            self._escolher(self.sel)
        elif tecla == K.ESCAPE:
            arcade.exit()

    def _escolher(self, i):
        if i == 0:
            from .tela_jogo import TelaJogo
            audio.parar_musica()
            self.window.show_view(TelaJogo(0, Progresso()))
        elif i == 1:
            self._ranking()
        elif i == 2:
            self.mostrar_controles = True
        else:
            arcade.exit()

    def _ranking(self):
        from .tela_ranking import TelaRanking
        audio.tocar("menu_ok")
        self.window.show_view(TelaRanking(voltar=TelaInicial))

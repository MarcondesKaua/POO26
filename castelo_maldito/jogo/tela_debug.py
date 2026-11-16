"""Menu de teste (Alt+L): pula direto para qualquer fase, inclusive a etapa 2 do chefe.

Funciona no menu inicial, durante o jogo e na tela entre fases. Para desativar no jogo final, basta apagar as
chamadas de atalho_debug() nas telas.
"""
import arcade

from . import recursos, ui
from .audio import audio
from .config import ALTURA, BRANCO, CINZA, FASES, LARGURA, OURO, VERDE
from .estado import Progresso

K = arcade.key


def atalho_debug(view, tecla, mods):
    """Chame no começo do on_key_press de uma tela: Alt+L abre o menu de testes. Retorna True se tratou a tecla."""
    alt = K.MOD_ALT | getattr(K, "MOD_OPTION", 0)
    if tecla == K.L and mods & alt:
        view.window.show_view(TelaDebug(view))
        return True
    return False


class TelaDebug(arcade.View):
    def __init__(self, anterior=None):
        super().__init__()
        self.anterior = anterior          # tela de onde veio (volta para ela ao fechar)
        self.sel = 0
        self.equipado = True              # começa com equipamento completo (é um menu de teste)
        # (rótulo, indice_da_fase, comecar_na_etapa_2_do_chefe)
        self.destinos = [(f"Fase {i + 1}: {FASES[i][2]}", i, False) for i in range(len(FASES))]
        self.destinos.append(("Chefe: começar direto na etapa 2 (sobreviver)", 3, True))
        self.linha_toggle = len(self.destinos)
        self.linha_voltar = len(self.destinos) + 1
        self.total = len(self.destinos) + 2

    def on_show_view(self):
        self.window.background_color = (0, 0, 0, 255)

    # ------------------------------------------------------------------ ações
    def _ir(self, indice, etapa2):
        from .tela_jogo import TelaJogo
        prog = Progresso()
        if self.equipado:
            prog.armas = [0, 1, 2, 3]
            prog.subs = ["machado", "agua"]
            prog.sub_atual = 0
            prog.coracoes = 99
            prog.vidas = 9
        audio.tocar("menu_ok")
        audio.parar_musica()
        self.window.show_view(TelaJogo(indice, prog, fase2=etapa2))

    def _fechar(self):
        audio.tocar("menu_ok")
        if self.anterior is not None:
            self.window.show_view(self.anterior)
        else:
            from .tela_inicio import TelaInicial
            self.window.show_view(TelaInicial())

    def _escolher(self, linha):
        if linha < len(self.destinos):
            _, indice, etapa2 = self.destinos[linha]
            self._ir(indice, etapa2)
        elif linha == self.linha_toggle:
            self.equipado = not self.equipado
            audio.tocar("menu_move")
        else:
            self._fechar()

    # ------------------------------------------------------------------ teclado
    def on_key_press(self, tecla, mods):
        alt = K.MOD_ALT | getattr(K, "MOD_OPTION", 0)
        if tecla == K.ESCAPE or (tecla == K.L and mods & alt):
            self._fechar()
        elif tecla in (K.UP, K.W):
            self.sel = (self.sel - 1) % self.total
            audio.tocar("menu_move")
        elif tecla in (K.DOWN, K.S):
            self.sel = (self.sel + 1) % self.total
            audio.tocar("menu_move")
        elif tecla in (K.LEFT, K.RIGHT, K.A, K.D) and self.sel == self.linha_toggle:
            self._escolher(self.linha_toggle)
        elif tecla in (K.ENTER, K.RETURN, K.SPACE):
            self._escolher(self.sel)
        elif K.KEY_1 <= tecla < K.KEY_1 + len(self.destinos):      # teclas 1..6 pulam direto
            self.sel = tecla - K.KEY_1
            self._escolher(self.sel)

    # ------------------------------------------------------------------ desenho
    def on_draw(self):
        self.clear()
        ui.camera_padrao()
        ui.textura(recursos.textura("bg", "titulo.png"), LARGURA / 2, ALTURA / 2, LARGURA, ALTURA)
        ui.fundo_escuro(225)
        ui.texto_sombra("MENU DE TESTE", LARGURA / 2, ALTURA - 70, OURO, 32, "center")
        ui.texto("Alt+L abre/fecha   ↑ ↓ navegar   ENTER escolher   1-6 atalho direto   ESC voltar",
                 LARGURA / 2, ALTURA - 100, CINZA, 13, "center")
        for i in range(self.total):
            y = ALTURA - 160 - i * 40
            ativo = i == self.sel
            if i < len(self.destinos):
                txt, cor = f"{i + 1}.  {self.destinos[i][0]}", OURO if ativo else BRANCO
            elif i == self.linha_toggle:
                txt = f"Equipamento completo (espadas, sub-armas, 99 corações, 9 vidas): {'SIM' if self.equipado else 'NÃO'}"
                cor = VERDE if self.equipado else CINZA
                if ativo:
                    cor = OURO
            else:
                txt, cor = "Voltar", OURO if ativo else CINZA
            if ativo:
                ui.retangulo(120, y - 10, LARGURA - 240, 34, (255, 255, 255, 28))
                ui.texto_sombra(">", 135, y, OURO, 20)
            ui.texto(txt, 170, y, cor, 18)

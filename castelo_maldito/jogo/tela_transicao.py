"""Tela entre fases: resumo parcial e início da próxima fase."""
import arcade

from . import recursos, ui
from .audio import audio
from .config import ALTURA, BRANCO, CINZA, FASES, LARGURA, OURO
from .tela_debug import atalho_debug

K = arcade.key


class TelaTransicao(arcade.View):
    def __init__(self, proxima, progresso):
        super().__init__()
        self.proxima = proxima
        self.prog = progresso
        self.t = 0.0

    def on_show_view(self):
        self.window.background_color = (0, 0, 0, 255)

    def on_update(self, dt):
        self.t += dt
        if self.t > 12:
            self._seguir()

    def _seguir(self):
        from .tela_jogo import TelaJogo
        self.window.show_view(TelaJogo(self.proxima, self.prog))

    def on_key_press(self, tecla, mods):
        if atalho_debug(self, tecla, mods):     # Alt+L: menu de testes
            return
        if tecla in (K.ENTER, K.RETURN, K.SPACE) and self.t > 0.5:
            audio.tocar("menu_ok")
            self._seguir()

    def on_draw(self):
        self.clear()
        ui.camera_padrao()
        ui.textura(recursos.textura("bg", "titulo.png"), LARGURA / 2, ALTURA / 2, LARGURA, ALTURA)
        ui.fundo_escuro(200)
        p = self.prog
        ui.texto_sombra("FASE CONCLUÍDA!", LARGURA / 2, ALTURA - 130, OURO, 42, "center")
        ui.texto(f"Pontos: {p.pontos}", LARGURA / 2, 340, BRANCO, 22, "center")
        ui.texto(f"Tempo: {int(p.tempo) // 60:02d}:{int(p.tempo) % 60:02d}    Inimigos: {p.abates}    Mortes: {p.mortes}",
                 LARGURA / 2, 305, CINZA, 17, "center")
        nome = FASES[self.proxima][2]
        ui.texto("Próxima:", LARGURA / 2, 240, CINZA, 16, "center")
        ui.texto_sombra(nome, LARGURA / 2, 205, (255, 130, 150, 255) if self.proxima == 3 else BRANCO, 26, "center")
        if int(self.t * 2) % 2 == 0:
            ui.texto("[ENTER] continuar", LARGURA / 2, 110, OURO, 18, "center")

"""TelaRanking: exibe o Top 10 salvo no banco (consulta feita UMA vez, no __init__)."""
import arcade

from . import recursos, ui
from .audio import audio
from .config import ALTURA, BRANCO, CINZA, LARGURA, OURO, VERMELHO
from .modelos import Pontuacao

K = arcade.key

# posições X (alinhamento das colunas) e espaçamento vertical entre linhas
COL_POS, COL_NOME, COL_PONTOS, COL_TEMPO, COL_DATA = 150, 190, 560, 680, 730
Y_PRIMEIRA = 390
ESPACO = 34
CORES_PODIO = [(255, 215, 80, 255), (210, 215, 230, 255), (215, 150, 90, 255)]


class TelaRanking(arcade.View):
    def __init__(self, voltar=None, destaque_id=None):
        super().__init__()
        self.voltar = voltar
        self.destaque_id = destaque_id
        self.erro = None
        # Consulta única (fora do on_draw): os 10 melhores por pontos, em ordem decrescente.
        try:
            self.melhores = list(Pontuacao.select().order_by(Pontuacao.pontos.desc()).limit(10))
        except Exception as e:
            self.melhores = []
            self.erro = str(e)

    def on_show_view(self):
        self.window.background_color = (0, 0, 0, 255)
        audio.musica("musica_menu")

    def on_draw(self):
        self.clear()
        ui.camera_padrao()
        ui.textura(recursos.textura("bg", "titulo.png"), LARGURA / 2, ALTURA / 2, LARGURA, ALTURA)
        ui.fundo_escuro(215)
        arcade.draw_text("RANKING - TOP 10", LARGURA / 2, ALTURA - 80, OURO, 38, anchor_x="center", bold=True)

        if self.erro:
            arcade.draw_text("Erro ao ler o banco de dados.", LARGURA / 2, ALTURA / 2, VERMELHO, 20, anchor_x="center")
        elif not self.melhores:
            arcade.draw_text("Nenhuma pontuação registrada ainda.", LARGURA / 2, ALTURA / 2 + 20, BRANCO, 22,
                             anchor_x="center")
            arcade.draw_text("Termine uma partida para entrar no ranking!", LARGURA / 2, ALTURA / 2 - 20, CINZA, 16,
                             anchor_x="center")
        else:
            y_cab = Y_PRIMEIRA + 40
            arcade.draw_text("#", COL_POS, y_cab, CINZA, 14, anchor_x="right", bold=True)
            arcade.draw_text("JOGADOR", COL_NOME, y_cab, CINZA, 14, bold=True)
            arcade.draw_text("PONTOS", COL_PONTOS, y_cab, CINZA, 14, anchor_x="right", bold=True)
            arcade.draw_text("TEMPO", COL_TEMPO, y_cab, CINZA, 14, anchor_x="right", bold=True)
            arcade.draw_text("DATA", COL_DATA, y_cab, CINZA, 14, bold=True)
            for i, reg in enumerate(self.melhores):
                y = Y_PRIMEIRA - i * ESPACO          # Y proporcional ao índice
                cor = CORES_PODIO[i] if i < 3 else BRANCO
                if reg.id == self.destaque_id:
                    ui.retangulo(COL_POS - 50, y - 8, 700, 30, (255, 255, 255, 40))
                arcade.draw_text(f"{i + 1}º", COL_POS, y, cor, 18, anchor_x="right", bold=True)
                arcade.draw_text(reg.nome_jogador, COL_NOME, y, cor, 18, bold=True)
                arcade.draw_text(str(reg.pontos), COL_PONTOS, y, cor, 18, anchor_x="right", bold=True)
                t = reg.tempo_partida
                arcade.draw_text(f"{int(t) // 60:02d}:{int(t) % 60:02d}", COL_TEMPO, y, cor, 18, anchor_x="right")
                arcade.draw_text(reg.data_hora.strftime("%d/%m/%Y"), COL_DATA, y, CINZA, 16)
        arcade.draw_text("[ESC] / [ENTER] voltar", LARGURA / 2, 30, CINZA, 14, anchor_x="center")

    def on_key_press(self, tecla, mods):
        if tecla in (K.ESCAPE, K.ENTER, K.RETURN, K.BACKSPACE, K.R):
            audio.tocar("menu_ok")
            if self.voltar is not None:
                self.window.show_view(self.voltar())
            else:
                from .tela_inicio import TelaInicial
                self.window.show_view(TelaInicial())

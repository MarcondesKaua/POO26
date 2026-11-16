"""Fim de partida: captura o nome do jogador (on_text / on_key_press) e grava a pontuação com Peewee."""
import arcade

from . import recursos, ui
from .audio import audio
from .config import ALTURA, BRANCO, CINZA, LARGURA, OURO, VERDE, VERMELHO
from .estado import Progresso
from .modelos import Pontuacao

K = arcade.key
MAX_NOME = 12


class TelaGameOver(arcade.View):
    def __init__(self, progresso):
        super().__init__()
        self.prog = progresso
        self.nome = ""
        self.estado = "digitando"      # digitando -> salvo
        self.registro = None
        self.erro = None
        self.t = 0.0

    def on_show_view(self):
        self.window.background_color = (0, 0, 0, 255)

    def on_update(self, dt):
        self.t += dt

    # ------------------------------------------------------------------ persistência (CREATE)
    def _salvar(self):
        nome = self.nome.strip() or "ANÔNIMO"
        try:
            self.registro = Pontuacao.create(nome_jogador=nome, pontos=self.prog.pontos,
                                             tempo_partida=round(self.prog.tempo, 1))
            print("[ranking] salvo:", self.registro)   # usa Pontuacao.__str__
        except Exception as e:   # banco bloqueado, disco cheio...
            self.erro = str(e)
            print("[ranking] erro ao salvar:", e)
        self.estado = "salvo"
        audio.tocar("menu_ok")

    # ------------------------------------------------------------------ teclado
    def on_text(self, texto):
        if self.estado != "digitando":
            return
        for ch in texto:
            if ch.isprintable() and ord(ch) < 0x250 and len(self.nome) < MAX_NOME:
                self.nome += ch

    def on_key_press(self, tecla, mods):
        if self.estado == "digitando":
            if tecla == K.BACKSPACE:
                self.nome = self.nome[:-1]
            elif tecla in (K.ENTER, K.RETURN):
                self._salvar()
            elif tecla == K.ESCAPE:   # pular sem salvar
                self._menu()
            return
        if tecla == K.R:
            from .tela_inicio import TelaInicial
            from .tela_ranking import TelaRanking
            audio.tocar("menu_ok")
            destaque = self.registro.id if self.registro is not None else None
            self.window.show_view(TelaRanking(voltar=TelaInicial, destaque_id=destaque))
        elif tecla in (K.ENTER, K.RETURN):
            self._jogar_de_novo()
        elif tecla == K.ESCAPE:
            self._menu()

    def _jogar_de_novo(self):
        from .tela_jogo import TelaJogo
        audio.parar_musica()
        self.window.show_view(TelaJogo(0, Progresso()))

    def _menu(self):
        from .tela_inicio import TelaInicial
        self.window.show_view(TelaInicial())

    # ------------------------------------------------------------------ desenho
    def on_draw(self):
        self.clear()
        ui.camera_padrao()
        ui.textura(recursos.textura("bg", "titulo.png"), LARGURA / 2, ALTURA / 2, LARGURA, ALTURA)
        ui.fundo_escuro(215)
        p = self.prog
        if p.venceu:
            ui.texto_sombra("VITÓRIA!", LARGURA / 2, ALTURA - 100, OURO, 54, "center")
            ui.texto("O Conde Vorthal foi destruído e o castelo está em paz.", LARGURA / 2, ALTURA - 140, BRANCO, 16, "center")
        else:
            ui.texto_sombra("FIM DE JOGO", LARGURA / 2, ALTURA - 100, VERMELHO, 54, "center")
        ui.texto(f"Pontos: {p.pontos}", LARGURA / 2, 370, OURO, 26, "center")
        ui.texto(f"Tempo: {int(p.tempo) // 60:02d}:{int(p.tempo) % 60:02d}   Inimigos: {p.abates}   Mortes: {p.mortes}",
                 LARGURA / 2, 335, CINZA, 16, "center")
        if self.estado == "digitando":
            ui.texto("Digite seu nome e pressione ENTER:", LARGURA / 2, 270, BRANCO, 18, "center")
            ui.retangulo(LARGURA / 2 - 170, 205, 340, 46, (20, 12, 34, 255))
            ui.contorno(LARGURA / 2 - 170, 205, 340, 46, OURO, 2)
            cursor = "_" if int(self.t * 2) % 2 == 0 else " "
            ui.texto(self.nome + cursor, LARGURA / 2, 217, BRANCO, 24, "center")
            ui.texto("[ESC] pular sem salvar", LARGURA / 2, 150, CINZA, 13, "center")
        else:
            if self.erro:
                ui.texto("Não foi possível salvar no ranking.", LARGURA / 2, 270, VERMELHO, 18, "center")
            else:
                ui.texto(f"Pontuação de {self.registro.nome_jogador} salva no ranking!", LARGURA / 2, 270, VERDE, 18, "center")
            ui.texto("[R] ver ranking      [ENTER] jogar de novo      [ESC] menu", LARGURA / 2, 190, OURO, 17, "center")


"""Castelo Maldito - ponto de entrada.  Execute:  python main.py"""
import arcade

from jogo.config import ALTURA, LARGURA, TITULO
from jogo.modelos import iniciar_banco
from jogo.tela_inicio import TelaInicial


def main():
    iniciar_banco()   # abre ranking.db e cria a tabela Pontuacao se necessário
    janela = arcade.Window(LARGURA, ALTURA, TITULO, update_rate=1 / 60)
    janela.show_view(TelaInicial())
    arcade.run()


if __name__ == "__main__":
    main()

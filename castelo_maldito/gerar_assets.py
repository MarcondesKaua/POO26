"""Gera TODOS os sprites, tiles, fundos, sons e músicas do jogo (rode uma vez: python gerar_assets.py).

Tudo é desenhado/sintetizado por código (Pillow + numpy + wave), então não há arquivos externos
nem problemas de direitos autorais. Os assets já vêm prontos na pasta assets/, mas você pode
editar os scripts da pasta gerador/ e rodar de novo para mudar o visual ou o som.
"""
import time

from gerador import cenario, som, sprites
from gerador.pix import salvar_manifesto

if __name__ == "__main__":
    t0 = time.time()
    print("Desenhando sprites e tiles...")
    sprites.gerar_tudo()
    print("Desenhando fundos, título e logo...")
    cenario.gerar_tudo()
    print("Sintetizando sons e músicas...")
    som.gerar_tudo()
    salvar_manifesto()
    print(f"Pronto em {time.time() - t0:.1f}s -> pasta assets/")

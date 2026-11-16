"""Gerenciador de áudio. Qualquer falha de áudio é ignorada (o jogo continua mudo)."""
import os

import arcade

from .config import ASSETS


class Audio:
    def __init__(self):
        self._sons = {}
        self._player_musica = None
        self.musica_atual = None
        self.vol_efeitos = 0.55
        self.vol_musica = 0.40
        self.mudo = False
        self._falhou = False

    def _carregar(self, sub, nome):
        chave = (sub, nome)
        if chave not in self._sons:
            try:
                self._sons[chave] = arcade.load_sound(os.path.join(ASSETS, sub, nome + ".wav"))
            except Exception as e:  # sem dispositivo de áudio, arquivo ausente...
                if not self._falhou:
                    print("[audio] não foi possível carregar sons:", e)
                    self._falhou = True
                self._sons[chave] = None
        return self._sons[chave]

    def tocar(self, nome, volume=1.0):
        if self.mudo:
            return
        som = self._carregar("sons", nome)
        if som is None:
            return
        try:
            arcade.play_sound(som, volume=self.vol_efeitos * volume)
        except Exception:
            pass

    def musica(self, nome, repetir=True):
        if nome == self.musica_atual and self._player_musica is not None:
            return
        self.parar_musica()
        self.musica_atual = nome
        som = self._carregar("musica", nome)
        if som is None:
            return
        try:
            self._player_musica = arcade.play_sound(som, volume=0.0 if self.mudo else self.vol_musica, loop=repetir)
        except Exception:
            self._player_musica = None

    def parar_musica(self):
        if self._player_musica is not None:
            try:
                arcade.stop_sound(self._player_musica)
            except Exception:
                pass
        self._player_musica = None
        self.musica_atual = None

    def alternar_mudo(self):
        self.mudo = not self.mudo
        if self._player_musica is not None:
            try:
                self._player_musica.volume = 0.0 if self.mudo else self.vol_musica
            except Exception:
                pass
        return self.mudo


audio = Audio()

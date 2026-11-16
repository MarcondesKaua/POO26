"""Carregamento (com cache) de texturas e folhas de sprites.

As folhas de sprites são fatiadas com arcade.load_spritesheet() + get_texture_grid(),
como pede o enunciado. Cada folha tem uma versão espelhada (_l) para o personagem olhar à esquerda.
"""
import json
import os

import arcade

from .config import ASSETS

_manifesto = None
_texturas = {}
_quadros = {}


def caminho(*partes):
    return os.path.join(ASSETS, *partes)


def manifesto():
    global _manifesto
    if _manifesto is None:
        with open(caminho("manifesto.json"), encoding="utf-8") as f:
            _manifesto = json.load(f)
    return _manifesto


def _algoritmo_caixa():
    """Hit box = retângulo da imagem inteira (estável entre os quadros da animação)."""
    try:
        return arcade.hitbox.algo_bounding_box
    except Exception:
        return None


def textura(sub, nome, caixa=False):
    chave = (sub, nome, caixa)
    if chave not in _texturas:
        arq = caminho(sub, nome)
        alg = _algoritmo_caixa() if caixa else None
        if alg is not None:
            try:
                _texturas[chave] = arcade.load_texture(arq, hit_box_algorithm=alg)
                return _texturas[chave]
            except Exception:
                pass
        _texturas[chave] = arcade.load_texture(arq)
    return _texturas[chave]


def _fatiar(arquivo, w, h, colunas, total):
    """Fatia uma folha de sprites em texturas (Arcade 3.x: SpriteSheet.get_texture_grid)."""
    try:
        folha = arcade.load_spritesheet(arquivo)
    except TypeError:  # versões antigas exigiam todos os argumentos
        return arcade.load_spritesheet(arquivo, w, h, colunas, total)
    alg = _algoritmo_caixa()
    if alg is not None:
        try:
            return folha.get_texture_grid(size=(w, h), columns=colunas, count=total, hit_box_algorithm=alg)
        except TypeError:
            pass
    return folha.get_texture_grid(size=(w, h), columns=colunas, count=total)


def quadros(chave):
    """Retorna (quadros_direita, quadros_esquerda) para 'sprites/nome'."""
    if chave not in _quadros:
        w, h, total, colunas = manifesto()[chave]
        direita = _fatiar(caminho(chave + ".png"), w, h, colunas, total)
        esquerda = _fatiar(caminho(chave + "_l.png"), w, h, colunas, total)
        # a folha espelhada tem os quadros na mesma ordem (cada quadro foi espelhado individualmente)
        _quadros[chave] = (list(direita), list(esquerda))
    return _quadros[chave]


def tamanho_quadro(chave):
    w, h, _, _ = manifesto()[chave]
    return w, h

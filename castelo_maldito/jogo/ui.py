"""Funções de desenho reutilizáveis (retângulos, textos com cache, texturas)."""
import arcade

from .config import BRANCO, PRETO

_cache_textos = {}

try:
    from arcade.types import Color as _Color
except Exception:  # versões antigas do arcade
    _Color = None


def _cor(c):
    """O Arcade 3.x exige objetos Color (e não tuplas) em várias funções de desenho."""
    if _Color is None:
        return c
    if len(c) == 3:
        c = (*c, 255)
    return _Color(*[int(v) for v in c])


def camera_padrao():
    """Volta para a câmera padrão (coordenadas de tela)."""
    try:
        arcade.get_window().default_camera.use()
    except Exception:
        pass


def retangulo(x, y, w, h, cor):
    if hasattr(arcade, "draw_lbwh_rectangle_filled"):
        arcade.draw_lbwh_rectangle_filled(x, y, w, h, _cor(cor))
    else:
        arcade.draw_rectangle_filled(x + w / 2, y + h / 2, w, h, cor)


def contorno(x, y, w, h, cor, largura=2):
    if hasattr(arcade, "draw_lbwh_rectangle_outline"):
        arcade.draw_lbwh_rectangle_outline(x, y, w, h, _cor(cor), largura)
    else:
        arcade.draw_rectangle_outline(x + w / 2, y + h / 2, w, h, cor, largura)


def textura(tex, cx, cy, w=None, h=None, cor=BRANCO, angulo=0.0):
    w = w or tex.width
    h = h or tex.height
    if hasattr(arcade, "draw_texture_rect"):
        arcade.draw_texture_rect(tex, arcade.XYWH(cx, cy, w, h), color=_cor(cor), angle=angulo)
    else:
        arcade.draw_texture_rectangle(cx, cy, w, h, tex, angulo, cor[3] if len(cor) > 3 else 255)


def texto(txt, x, y, cor=BRANCO, tam=16, ax="left", ay="baseline", negrito=True):
    """Texto com cache de arcade.Text (bem mais rápido que recriar a cada frame)."""
    chave = (str(txt), tuple(cor), tam, ax, ay, negrito)
    t = _cache_textos.get(chave)
    if t is None:
        if len(_cache_textos) > 600:
            _cache_textos.clear()
        t = arcade.Text(str(txt), x, y, _cor(cor), tam, anchor_x=ax, anchor_y=ay, bold=negrito)
        _cache_textos[chave] = t
    t.x = x
    t.y = y
    t.draw()


def texto_sombra(txt, x, y, cor=BRANCO, tam=16, ax="left", ay="baseline"):
    texto(txt, x + 2, y - 2, PRETO, tam, ax, ay)
    texto(txt, x, y, cor, tam, ax, ay)


def fundo_escuro(alpha=170):
    retangulo(0, 0, 1024, 576, (0, 0, 0, alpha))

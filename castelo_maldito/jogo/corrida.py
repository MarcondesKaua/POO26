"""Fase de corrida: o Dodo (corredor rival), a largada, a linha de chegada e as regras da disputa.

O Dodo é desenhado por código (Pillow) na primeira vez que aparece (não precisa de arquivos em assets/).
Ele segue o MESMO percurso do jogador usando um piloto automático simples: corre para a direita, pula quando o chão
acaba, quando há parede ou espinhos à frente. A velocidade dele é um pouco menor que a do jogador (com arrancadas
rápidas de vez em quando e um "elástico" que o segura se estiver muito na frente ou o acelera se ficar muito para trás),
para que uma corrida limpa seja vencível e um erro ou dois ainda dê para recuperar.
"""
import arcade
from PIL import Image, ImageDraw

from . import ui
from .audio import audio
from .config import ALTURA, BRANCO, GRAVIDADE, FORCA_PULO, LARGURA, OURO, PRETO, TILE, VEL_QUEDA_MAX
from .corpo import CorpoGrade

# --------------------------------------------------------------------------------------------- arte do Dodo
_W, _H = 28, 26            # grade lógica; é ampliada 2x (56x52)
_OL = (14, 5, 18, 255)
_C = dict(
    corpo=(118, 130, 158, 255), sombra=(88, 98, 126, 255), barriga=(176, 184, 204, 255),
    asa=(92, 102, 130, 255), asa_luz=(140, 152, 180, 255), pena=(78, 88, 114, 255),
    bico=(238, 190, 72, 255), bico_esc=(196, 128, 40, 255), perna=(236, 188, 70, 255),
    perna_esc=(190, 130, 40, 255), faixa=(155, 35, 53, 255), faixa_luz=(205, 70, 82, 255),
    branco=(255, 255, 255, 255), pupila=(30, 14, 24, 255), topete=(190, 196, 214, 255),
)


def _perna(d, hx, hy, fx, fy, frente):
    c = _C["perna"] if frente else _C["perna_esc"]
    n = max(abs(fx - hx), abs(fy - hy), 1)
    for i in range(n + 1):
        x = round(hx + (fx - hx) * i / n)
        y = round(hy + (fy - hy) * i / n)
        d.point((x, y), fill=c)
        d.point((x + 1, y), fill=c)
    d.line([(fx, fy), (fx + 3, fy)], fill=c)
    d.point((fx + 3, fy - 1), fill=c)


def _quadro(i):
    """i: 0-3 = ciclo de corrida, 4 = no ar, 5 = parado."""
    img = Image.new("RGBA", (_W, _H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bob = 1 if i in (1, 3) else 0
    chao = 24
    trás = {0: (6, chao), 1: (9, chao - 1), 2: (13, chao), 3: (9, chao), 4: (8, 22), 5: (9, chao)}[i]
    frente = {0: (17, chao), 1: (14, chao), 2: (9, chao), 3: (14, chao - 1), 4: (16, 22), 5: (14, chao)}[i]
    _perna(d, 10, 18, trás[0], trás[1], False)
    for (x0, y0, x1, y1) in ((5, 11 - bob, 1, 7 - bob), (5, 12 - bob, 0, 11 - bob), (6, 10 - bob, 3, 5 - bob)):
        d.line([(x0, y0), (x1, y1)], fill=_C["pena"])                     # penas do rabo
    d.point((1, 6 - bob), fill=_C["topete"]); d.point((3, 4 - bob), fill=_C["topete"])
    d.ellipse([3, 7 - bob, 20, 20 - bob], fill=_C["corpo"])               # corpo
    d.ellipse([3, 13 - bob, 13, 20 - bob], fill=_C["sombra"])
    d.ellipse([8, 12 - bob, 19, 19 - bob], fill=_C["barriga"])
    ay = 8 if i == 4 else 10                                              # asa
    d.ellipse([6, ay - bob, 14, ay + 6 - bob], fill=_C["asa"])
    d.line([(7, ay + 1 - bob), (12, ay + 1 - bob)], fill=_C["asa_luz"])
    d.point((8, ay + 5 - bob), fill=_C["pena"]); d.point((10, ay + 6 - bob), fill=_C["pena"])
    d.rectangle([15, 7 - bob, 20, 11 - bob], fill=_C["corpo"])            # pescoço e cabeça
    d.ellipse([15, 2 - bob, 23, 10 - bob], fill=_C["corpo"])
    d.point((18, 2 - bob), fill=_C["topete"]); d.point((17, 3 - bob), fill=_C["topete"])
    d.line([(16, 4 - bob), (22, 4 - bob)], fill=_C["faixa"])              # bandana vermelha
    d.line([(16, 4 - bob), (14, 5 - bob), (12, 5 - bob)], fill=_C["faixa"])
    d.point((13, 6 - bob), fill=_C["faixa_luz"]); d.point((19, 4 - bob), fill=_C["faixa_luz"])
    d.polygon([(22, 5 - bob), (26, 5 - bob), (27, 8 - bob), (26, 11 - bob), (23, 11 - bob), (22, 9 - bob)],
              fill=_C["bico"])                                            # bico grande e curvo
    d.line([(23, 10 - bob), (26, 10 - bob)], fill=_C["bico_esc"])
    d.point((27, 8 - bob), fill=_C["bico_esc"]); d.point((25, 6 - bob), fill=_C["bico_esc"])
    d.point((20, 6 - bob), fill=_C["branco"]); d.point((21, 6 - bob), fill=_C["pupila"])
    _perna(d, 14, 18, frente[0], frente[1], True)
    src = img.copy()
    px, out = src.load(), img.load()
    for y in range(_H):
        for x in range(_W):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < _W and 0 <= ny < _H and px[nx, ny][3] > 0:
                        out[x, y] = _OL
                        break
    return img.resize((_W * 2, _H * 2), Image.NEAREST)


_texturas = None


def texturas_dodo():
    """(quadros_direita, quadros_esquerda): 0-3 corrida, 4 no ar, 5 parado. Cache em memória."""
    global _texturas
    if _texturas is None:
        dir_ = [_quadro(i) for i in range(6)]
        esq = [im.transpose(Image.FLIP_LEFT_RIGHT) for im in dir_]
        _texturas = ([arcade.Texture(im) for im in dir_], [arcade.Texture(im) for im in esq])
    return _texturas


# --------------------------------------------------------------------------------------------- o Dodo
class Dodo(CorpoGrade):
    meia_l = 18
    meia_a = 26

    VEL_BASE = 6.5           # px/frame (o jogador anda a 4.6 x 1.4 = 6.44 na corrida, fora o dash)
    SPRINT_MULT = 1.45       # arrancada
    SPRINT_CICLO = 4.5       # a cada 4.5 s ...
    SPRINT_DURACAO = 1.3     # ... ele acelera por 1.3 s

    def __init__(self, x, y_pes):
        self.quadros = texturas_dodo()[0]
        super().__init__(self.quadros[5], x, y_pes + self.meia_a + 1)
        self.largada = (x, y_pes + self.meia_a + 1)
        self.reiniciar()

    def reiniciar(self):
        self.center_x, self.center_y = self.largada
        self.vy = 0.0
        self.no_chao = False
        self.ciclo = self.SPRINT_CICLO - self.SPRINT_DURACAO + 0.3   # começa com uma arrancada logo após o "JÁ!"
        self.ult_chao = self.largada
        self.tropecou = 0.0
        self.tentativas = 0
        self.queda_x = -1e9
        self.i = 0
        self.t_anim = 0.0
        self.vel_atual = 0.0
        self.frames_ar = 0
        self.corte = None
        self.vx_ar = 0.0
        self.texture = self.quadros[5]

    # ------------------------------------------------------------------ piloto automático
    def _decidir(self, mapa, vx):
        """None = seguir correndo; 'buraco' ou 'obstaculo' = pular."""
        l, b, r, t = self.caixa
        # 1) o chão acaba logo à frente: degrau para baixo (até 3 tiles) é só andar; senão é buraco
        x_pe = r - 8 + vx * 1.5
        if not mapa.solido_em(x_pe, b - 4):
            if any(mapa.solido_em(x_pe, b - 4 - k * TILE) for k in (1, 2, 3)):
                return None
            return "buraco"
        # 2) parede ou degrau à frente
        alc = 10 + vx * 8
        for dy in (4, 36, 70):
            if mapa.solido_em(r + alc, b + dy):
                return "obstaculo"
        # 3) espinhos à frente
        if mapa.espinho_em(r + 4 + vx * 5, b + 4):
            return "obstaculo"
        return None

    def _simular_pulo(self, mapa, vx, corte):
        """Simula o pulo (com a mesma física) e devolve o x onde ele pousa em segurança, ou None se bater/cair."""
        ml, ma = self.meia_l, self.meia_a
        x, y, vy = self.center_x, self.center_y, FORCA_PULO
        for f in range(1, 110):
            if corte is not None and f >= corte and vy > 4:
                vy *= 0.55
            vy = max(vy - GRAVIDADE, -VEL_QUEDA_MAX)
            nx = x + vx
            if mapa.colide(nx - ml, y - ma, nx + ml, y + ma):
                return None                                   # bateria numa parede
            x = nx
            ny = y + vy
            if mapa.colide(x - ml, ny - ma, x + ml, ny + ma):
                if vy > 0:
                    vy, ny = 0.0, y                           # bateu a cabeça
                else:                                         # pousou: tem chão suficiente embaixo e sem espinhos?
                    pe = (int((ny - ma) // TILE) + 1) * TILE
                    apoio = sum(mapa.solido_em(x + dx, pe - 4) for dx in (-ml * 0.6, 0, ml * 0.6))
                    espinho = mapa.espinho_em(x - ml, pe + 4) or mapa.espinho_em(x + ml, pe + 4)
                    return x if apoio >= 2 and not espinho else None
            y = ny
        return None

    def _planejar_pulo(self, mapa, vx):
        """Escolhe (corte, escala): o pulo (cheio ou curto) que pousa em segurança mais à frente.
        Se em velocidade total não houver pouso seguro (ilha curta), o Dodo "freia" um pouco no ar (escala < 1)."""
        for escala in (1.0, 0.8, 0.65, 0.5):
            melhor, melhor_x = None, -1e9
            for corte in (None, 12, 10, 8, 6, 5, 4, 3, 2):
                x = self._simular_pulo(mapa, vx * escala, corte)
                if x is not None and x > melhor_x:
                    melhor, melhor_x = corte, x
            if melhor_x > -1e9:
                return melhor, escala
        return None, 1.0

    def ia(self, dt, jogo):
        mapa = jogo.mapa
        corrida = jogo.corrida
        vx = 0.0
        if corrida.estado == "valendo" and self.tropecou <= 0:
            self.ciclo = (self.ciclo + dt) % self.SPRINT_CICLO
            sprint = self.SPRINT_MULT if self.ciclo >= self.SPRINT_CICLO - self.SPRINT_DURACAO else 1.0
            dx = jogo.jogador.center_x - self.center_x          # "elástico": segura se está muito na frente ...
            elastico = 1.0 + max(-0.10, min(0.05, (dx - 100) * 0.0004))   # ... e acelera só um pouco se ficou para trás
            vx = self.VEL_BASE * sprint * elastico
            if self.no_chao:
                tipo = self._decidir(mapa, vx)
                if tipo:
                    self.vy = FORCA_PULO
                    self.frames_ar = 0
                    self.corte, escala = self._planejar_pulo(mapa, vx)
                    self.vx_ar = vx * escala                      # a velocidade do pulo fica travada até pousar
            if not self.no_chao or tipo:
                vx = self.vx_ar
        elif self.tropecou > 0:
            self.tropecou -= dt
        self.vel_atual = vx
        self.frames_ar += 1
        if self.corte is not None and self.frames_ar >= self.corte and self.vy > 4:
            self.vy *= 0.55                                       # "soltou o botão": pulo mais curto
        self.vy = max(self.vy - GRAVIDADE, -VEL_QUEDA_MAX)
        self.mover_grade(mapa, vx, self.vy)
        if self.bateu_x and self.no_chao and vx:
            self.vy = FORCA_PULO                                  # bateu numa parede: pula
            self.corte = None
            self.vx_ar = vx
        if self.no_chao:
            self.corte = None
            self.ult_chao = (self.center_x, self.center_y)
            if self.center_x > self.queda_x + 320:
                self.tentativas = 0
        if self.center_y < -80:                                   # caiu: volta ao último chão firme e perde um tempo
            self.center_x, self.center_y = self.ult_chao
            self.vy = 0.0
            self.tropecou = 0.8
            self.tentativas += 1
            self.queda_x = self.center_x
        self._animar(dt, vx)

    def _animar(self, dt, vx):
        if not self.no_chao:
            idx = 4
        elif vx <= 0:
            idx = 5
        else:
            self.t_anim += dt * (vx / 5.0)
            if self.t_anim >= 0.09:
                self.t_anim = 0.0
                self.i = (self.i + 1) % 4
            idx = self.i
        self.texture = self.quadros[idx]


# --------------------------------------------------------------------------------------------- a corrida
class Corrida:
    """Largada (3, 2, 1, JÁ!), regras de vitória/derrota, queda em buracos e a linha de chegada."""

    PREMIO = 2000            # pontos extras ao vencer (o bônus final de vidas/vida também é somado)

    def __init__(self, jogo):
        self.jogo = jogo
        cfg = jogo.mapa.corrida
        self.fim_x = cfg["fim"] * TILE
        self.inicio_x = jogo.ponto_respawn[0]
        dc, dr = cfg["dodo"]
        self.dodo = Dodo(dc * TILE + TILE / 2, dr * TILE)
        self.lista = arcade.SpriteList()
        self.lista.append(self.dodo)
        self.estado = "contagem"          # contagem -> valendo -> venceu | perdeu
        self.t = 0.0
        self.espera = 1.0
        self.t_go = 0.0
        self.tempo = 0.0                  # tempo de corrida (s)
        self.t_perdeu = 0.0
        self.ult_chao = jogo.ponto_respawn
        self.banner = None                # (texto, cor)

    # ------------------------------------------------------------------ regras
    def reiniciar(self, espera=0.6):
        j = self.jogo.jogador
        self.estado, self.t, self.espera, self.t_go, self.tempo = "contagem", 0.0, espera, 0.0, 0.0
        self.banner = None
        self.dodo.reiniciar()
        px, py = self.jogo.ponto_respawn
        j.center_x, j.center_y = px, py
        j.change_x = j.change_y = 0
        self.ult_chao = (px, py)
        self.jogo.cam_x = px
        self.jogo.entrada.limpar()

    def queda(self, j):
        """Caiu num buraco: volta ao último chão firme, perde um pouco de vida (nunca morre por isso) e tempo."""
        x, y = self.ult_chao
        j.center_x, j.center_y = x, y + 2
        j.change_x = j.change_y = 0
        j.invul = 1.0
        self.jogo.prog.vida = max(1, self.jogo.prog.vida - 2)
        audio.tocar("dano")
        self.jogo.tremer(0.2)

    def _espinho_embaixo(self, j):
        m = self.jogo.mapa
        y = j.center_y - 36 + 4
        return m.espinho_em(j.center_x - 12, y) or m.espinho_em(j.center_x + 12, y)

    def atualizar(self, dt):
        j = self.jogo.jogador
        self.t += dt
        if self.estado == "contagem":
            self.jogo.entrada.limpar()                     # parados até o "JÁ!"
            if self.t >= self.espera + 3.0:
                self.estado, self.t_go = "valendo", 0.0
                audio.tocar("menu_ok")
        elif self.estado == "valendo":
            self.t_go += dt
            self.tempo += dt
            if j.no_chao and j.change_y == 0 and not j.morto and not self._espinho_embaixo(j):
                self.ult_chao = (j.center_x, j.center_y)
            if not j.morto and j.center_x >= self.fim_x:
                self._vencer()
            elif self.dodo.center_x >= self.fim_x:
                self._perder()
        elif self.estado == "perdeu":
            self.t_perdeu += dt
            if self.t_perdeu >= 2.6:
                self.reiniciar()
        self.dodo.ia(dt, self.jogo)

    def _vencer(self):
        self.estado = "venceu"
        self.banner = ("VOCÊ VENCEU O DODO!", OURO)
        self.jogo.corrida_vencida(self.PREMIO)

    def _perder(self):
        self.estado = "perdeu"
        self.t_perdeu = 0.0
        self.banner = ("O DODO VENCEU!  Tente de novo...", (255, 110, 120, 255))
        audio.tocar("dano")

    # ------------------------------------------------------------------ desenho
    def progresso(self, x):
        return max(0.0, min(1.0, (x - self.inicio_x) / (self.fim_x - self.inicio_x)))

    def desenhar_mundo(self):
        """Linha de chegada quadriculada + o Dodo (dentro da câmera do mundo)."""
        if abs(self.fim_x - self.jogo.cam_x) < LARGURA / 2 + 40:
            for k in range(ALTURA // 16):
                for c in (0, 1):
                    cor = BRANCO if (k + c) % 2 == 0 else PRETO
                    ui.retangulo(self.fim_x - 16 + c * 16, k * 16, 16, 16, (*cor[:3], 210))
            ui.texto_sombra("CHEGADA", self.fim_x, 330, OURO, 18, "center")
        self.lista.draw()

    def desenhar_hud(self):
        """Barra de progresso (você x Dodo), contagem da largada e avisos."""
        w = 400
        x = 350                                                      # à direita do painel de vida
        ui.retangulo(x - 3, ALTURA - 52, w + 6, 18, (10, 6, 20, 230))
        ui.retangulo(x, ALTURA - 49, w, 12, (45, 36, 70, 255))
        ui.contorno(x - 3, ALTURA - 52, w + 6, 18, (200, 170, 90, 255), 2)
        for k in range(6):                                           # bandeirinha quadriculada no fim da barra
            ui.retangulo(x + w - 6, ALTURA - 49 + k * 2, 6, 2, BRANCO if k % 2 == 0 else PRETO)
        pj = self.progresso(self.jogo.jogador.center_x)
        pd = self.progresso(self.dodo.center_x)
        ui.textura(self.dodo.quadros[5], x + w * pd, ALTURA - 28, 28, 26)      # o Dodo "anda" sobre a barra
        ui.retangulo(x + w * pj - 3, ALTURA - 49, 6, 12, OURO)                 # marcador do jogador
        ui.texto_sombra("VOCÊ", x + w * pj, ALTURA - 66, OURO, 11, "center")
        if self.estado == "contagem" and self.t >= self.espera:
            n = 3 - int(self.t - self.espera)
            ui.texto_sombra(str(max(1, n)), LARGURA / 2, ALTURA / 2 - 80, OURO, 96, "center")
        elif self.estado == "valendo" and self.t_go < 0.9:
            ui.texto_sombra("JÁ!", LARGURA / 2, ALTURA / 2 - 80, (150, 255, 170, 255), 96, "center")
        if self.banner:
            ui.texto_sombra(self.banner[0], LARGURA / 2, ALTURA / 2 - 20, self.banner[1], 34, "center")
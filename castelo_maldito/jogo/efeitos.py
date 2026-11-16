"""Partículas e textos flutuantes simples."""
import random

from . import ui


class Efeitos:
    def __init__(self):
        self.particulas = []   # [x, y, vx, vy, vida, vida_max, cor, tam]
        self.textos = []       # [x, y, texto, vida, cor]

    def faiscas(self, x, y, cor, n=8, vel=4.0, vida=0.5, grav=0.25):
        for _ in range(n):
            self.particulas.append([x, y, random.uniform(-vel, vel), random.uniform(0, vel * 1.3),
                                    random.uniform(vida * 0.5, vida), vida, cor, random.randint(3, 6), grav])
        if len(self.particulas) > 400:
            del self.particulas[:100]

    def texto(self, x, y, txt, cor=(255, 240, 170, 255)):
        self.textos.append([x, y, txt, 1.0, cor])

    def atualizar(self, dt):
        vivas = []
        for p in self.particulas:
            p[4] -= dt
            if p[4] > 0:
                p[0] += p[2]
                p[1] += p[3]
                p[3] -= p[8]
                vivas.append(p)
        self.particulas = vivas
        vt = []
        for t in self.textos:
            t[3] -= dt
            t[1] += 0.8
            if t[3] > 0:
                vt.append(t)
        self.textos = vt

    def desenhar(self):
        for p in self.particulas:
            a = int(255 * max(0, p[4] / p[5]))
            c = (p[6][0], p[6][1], p[6][2], a)
            ui.retangulo(p[0] - p[7] / 2, p[1] - p[7] / 2, p[7], p[7], c)
        for t in self.textos:
            c = (t[4][0], t[4][1], t[4][2], int(255 * min(1, t[3] * 2)))
            ui.texto_sombra(t[2], t[0], t[1], c, 14, "center")

"""Sintetiza (com numpy) todos os efeitos sonoros e as músicas em estilo chiptune. Sem arquivos externos."""
import os
import wave

import numpy as np

from .pix import caminho

SR = 22050
RNG = np.random.default_rng(1234)

BASE_NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def midi(nome):
    return BASE_NOTAS[nome[:-1]] + 12 * (int(nome[-1]) + 1)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


# ----------------------------------------------------------------------------- formas de onda


def osc(tipo, f, dur, duty=0.5):
    n = max(1, int(SR * dur))
    t = np.arange(n) / SR
    if tipo == "ruido":
        return RNG.uniform(-1, 1, n)
    f_arr = f if isinstance(f, np.ndarray) else np.full(n, float(f))
    fase = np.cumsum(f_arr) / SR
    ph = fase % 1.0
    if tipo == "quad":
        return np.where(ph < duty, 1.0, -1.0)
    if tipo == "tri":
        return 4 * np.abs(ph - 0.5) - 1
    if tipo == "serra":
        return 2 * ph - 1
    return np.sin(2 * np.pi * fase)


def varredura(f0, f1, dur, curva=1.0):
    n = max(1, int(SR * dur))
    t = np.linspace(0, 1, n) ** curva
    return f0 + (f1 - f0) * t


def adsr(n, a=0.004, d=0.05, s=0.7, r=0.04):
    e = np.full(n, s)
    na = min(int(a * SR), n)
    if na > 0:
        e[:na] = np.linspace(0, 1, na)
    nd = min(int(d * SR), n - na)
    if nd > 0:
        e[na:na + nd] = np.linspace(1, s, nd)
    nr = min(int(r * SR), n)
    if nr > 0:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def decai(n, k=6.0):
    return np.exp(-np.linspace(0, k, n))


def passa_baixa(x, janela):
    if janela <= 1:
        return x
    return np.convolve(x, np.ones(janela) / janela, mode="same")


def salvar_wav(nome, x, sub="sons", pico=0.9):
    x = np.asarray(x, dtype=np.float64)
    m = np.max(np.abs(x))
    if m > 0:
        x = x / m * pico
    pcm = (x * 32767).astype(np.int16)
    with wave.open(caminho(sub, nome + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def seq(*partes):
    return np.concatenate(partes)


def nota(m, dur, tipo="quad", duty=0.5, **kw):
    n = int(SR * dur)
    return osc(tipo, hz(m), dur, duty)[:n] * adsr(n, **kw)


# ----------------------------------------------------------------------------- efeitos


def gerar_efeitos():
    def swing(dur, f0, f1, ruido, janela):
        n = int(SR * dur)
        r = passa_baixa(osc("ruido", 0, dur), janela) * np.sin(np.linspace(0, np.pi, n)) ** 1.5
        s = osc("seno", varredura(f0, f1, dur), dur) * 0.25 * np.sin(np.linspace(0, np.pi, n))
        return r * ruido + s

    salvar_wav("golpe", swing(0.22, 500, 220, 1.0, 6))
    salvar_wav("golpe_leve", swing(0.14, 900, 500, 0.9, 3))
    salvar_wav("golpe_pesado", swing(0.34, 300, 110, 1.1, 10))

    def acerto():
        n = int(SR * 0.16)
        return (osc("ruido", 0, 0.16) * decai(n, 9) * 0.8 + osc("seno", varredura(220, 60, 0.16), 0.16) * decai(n, 5))
    salvar_wav("acerto", acerto())
    _a = acerto()
    _g = osc("seno", varredura(90, 40, 0.35), 0.35) * decai(int(SR * 0.35), 4)
    salvar_wav("acerto_forte", np.pad(_a, (0, len(_g) - len(_a))) + _g)

    n = int(SR * 0.3)
    salvar_wav("inimigo_morre", osc("quad", varredura(700, 90, 0.3), 0.3, 0.25) * decai(n, 4) * 0.7 + osc("ruido", 0, 0.3) * decai(n, 7) * 0.5)
    n = int(SR * 0.32)
    salvar_wav("dano", osc("serra", varredura(320, 80, 0.32), 0.32) * decai(n, 3) + osc("ruido", 0, 0.32) * decai(n, 8) * 0.4)
    salvar_wav("pulo", osc("quad", varredura(280, 720, 0.13), 0.13, 0.25) * adsr(int(SR * 0.13), 0.002, 0.03, 0.6, 0.04) * 0.6)
    n = int(SR * 0.18)
    salvar_wav("dash", passa_baixa(osc("ruido", 0, 0.18), 8) * np.sin(np.linspace(0, np.pi, n)) * 1.0)
    salvar_wav("moeda", seq(nota(midi("E6"), 0.07), nota(midi("B6"), 0.16, r=0.1)) * 0.6)
    salvar_wav("coracao", seq(nota(midi("C6"), 0.06), nota(midi("E6"), 0.06), nota(midi("G6"), 0.12, r=0.08)) * 0.6)
    salvar_wav("comida", seq(nota(midi("G5"), 0.07, "tri"), nota(midi("C6"), 0.07, "tri"), nota(midi("E6"), 0.07, "tri"), nota(midi("G6"), 0.16, "tri", r=0.1)))
    salvar_wav("item_forte", seq(*[nota(midi(x), 0.08, "tri") for x in ("C5", "E5", "G5", "C6", "E6", "G6")], nota(midi("C7"), 0.3, "quad", 0.25, r=0.2) * 0.6))
    n = int(SR * 0.2)
    salvar_wav("vela", osc("ruido", 0, 0.2) * decai(n, 10) * 0.7 + osc("quad", varredura(1200, 600, 0.2), 0.2, 0.125) * decai(n, 6) * 0.4)
    n = int(SR * 0.25)
    salvar_wav("arremesso", osc("serra", varredura(500, 1100, 0.25), 0.25) * np.sin(np.linspace(0, np.pi, n)) * 0.5)
    n = int(SR * 0.4)
    salvar_wav("vidro", osc("ruido", 0, 0.4) * decai(n, 8) * 0.6 + osc("seno", 2400, 0.4) * decai(n, 9) * 0.4)
    n = int(SR * 0.5)
    salvar_wav("fogo", passa_baixa(osc("ruido", 0, 0.5), 12) * (np.sin(np.linspace(0, np.pi, n)) ** 0.7))
    n = int(SR * 0.22)
    salvar_wav("bola_fogo", passa_baixa(osc("ruido", 0, 0.22), 5) * decai(n, 3) + osc("seno", varredura(900, 300, 0.22), 0.22) * 0.2)
    n = int(SR * 0.7)
    salvar_wav("explosao", passa_baixa(osc("ruido", 0, 0.7), 14) * decai(n, 4) + osc("seno", varredura(120, 30, 0.7), 0.7) * decai(n, 3) * 0.8)
    n = int(SR * 1.1)
    vib = 1 + 0.04 * np.sin(np.linspace(0, 60, n))
    salvar_wav("rugido", osc("serra", varredura(110, 55, 1.1) * vib, 1.1) * adsr(n, 0.08, 0.3, 0.7, 0.4) * 0.7 + passa_baixa(osc("ruido", 0, 1.1), 6) * adsr(n, 0.1, 0.3, 0.6, 0.4) * 0.5)
    n = int(SR * 2.4)
    salvar_wav("chefe_morre", passa_baixa(osc("ruido", 0, 2.4), 18) * decai(n, 2.5) + osc("serra", varredura(220, 25, 2.4), 2.4) * decai(n, 2.0) * 0.6)
    n = int(SR * 0.06)
    salvar_wav("osso", osc("ruido", 0, 0.06) * decai(n, 6) * 0.6 + osc("quad", 1400, 0.06, 0.125) * decai(n, 8) * 0.4)
    salvar_wav("checkpoint", seq(*[nota(midi(x), 0.1, "tri") for x in ("A4", "C#5", "E5", "A5")], nota(midi("A5"), 0.25, "tri", r=0.2)))
    salvar_wav("menu_move", nota(midi("A5"), 0.05, "quad", 0.25) * 0.6)
    salvar_wav("menu_ok", seq(nota(midi("E5"), 0.06, "quad", 0.25), nota(midi("B5"), 0.12, "quad", 0.25)) * 0.6)
    salvar_wav("troca_arma", seq(osc("ruido", 0, 0.03) * 0.5, nota(midi("D6"), 0.06, "tri"), nota(midi("A6"), 0.08, "tri")) * 0.8)
    salvar_wav("sem_coracoes", seq(nota(midi("A3"), 0.08, "quad", 0.5), nota(midi("F3"), 0.12, "quad", 0.5)) * 0.5)
    salvar_wav("pilar_aviso", seq(*[nota(midi("E4"), 0.05, "quad", 0.5) * (1 if i % 2 == 0 else 0.3) for i in range(6)]) * 0.5)
    salvar_wav("teleporte", osc("seno", varredura(1400, 200, 0.35), 0.35) * np.sin(np.linspace(0, np.pi, int(SR * 0.35))) * 0.6)


# ----------------------------------------------------------------------------- músicas

PROG = [(0, "m"), (-4, "M"), (-2, "M"), (-5, "m"), (0, "m"), (-4, "M"), (-5, "M"), (-5, "M")]
TRIADE = {"m": (0, 3, 7), "M": (0, 4, 7)}

# melodia em la menor: (nota, duração em tempos)
MELODIA = [
    [("E5", 1), ("C5", .5), ("D5", .5), ("E5", 1), ("A4", 1)],
    [("F5", 1), ("E5", .5), ("D5", .5), ("C5", 1), ("A4", 1)],
    [("D5", 1), ("E5", .5), ("F5", .5), ("G5", 1), ("D5", 1)],
    [("E5", 1.5), ("D5", .5), ("B4", 1), ("G4", 1)],
    [("A4", .5), ("C5", .5), ("E5", .5), ("A5", .5), ("G5", 1), ("E5", 1)],
    [("F5", .5), ("A5", .5), ("C6", 1), ("A5", 1), ("F5", 1)],
    [("G#4", 1), ("B4", 1), ("D5", 1), ("B4", 1)],
    [("E5", 2), ("-", 1), ("G#4", .5), ("B4", .5)],
]


class Faixa:
    def __init__(self, bpm, compassos):
        self.bpm = bpm
        self.dt = 60.0 / bpm
        self.buf = np.zeros(int(compassos * 4 * self.dt * SR) + SR)
        self.compassos = compassos

    def add(self, t_tempos, amostras, vol):
        i = int(t_tempos * self.dt * SR)
        fim = min(len(self.buf), i + len(amostras))
        if fim > i:
            self.buf[i:fim] += amostras[:fim - i] * vol

    def final(self):
        n = int(self.compassos * 4 * self.dt * SR)
        return self.buf[:n]


def compor(bpm, transp, passes=2, estilo="normal", duty_lead=0.25, tonica=45):
    f = Faixa(bpm, 8 * passes)
    dt = f.dt
    tempo = 0.0
    for ps in range(passes):
        for b, (off, tipo) in enumerate(PROG):
            raiz = tonica + off + transp
            inicio = (ps * 8 + b) * 4
            # --- baixo (triângulo)
            if estilo == "chefe":
                padrao = [0, 0, 12, 0, 0, 12, 0, 7]
                passo = 0.5
            elif estilo == "calmo":
                padrao = [0, None, None, None, 7, None, None, None]
                passo = 1.0
            else:
                padrao = [0, 0, 12, 0, 0, 12, 7, 0]
                passo = 0.5
            for k, o in enumerate(padrao):
                if o is None:
                    continue
                n = nota(raiz + o, passo * dt * 0.9, "tri", r=0.02)
                f.add(inicio + k * passo, n, 0.55 if estilo != "calmo" else 0.5)
            # --- arpejo (quadrada fina)
            acorde = [raiz + 12 + x for x in TRIADE[tipo]] + [raiz + 24]
            passo_arp = 0.25 if estilo != "calmo" else 1.0
            for k in range(int(4 / passo_arp)):
                m = acorde[[0, 1, 2, 3, 2, 1][k % 6]] if estilo != "calmo" else acorde[k % 4]
                n = nota(m, passo_arp * dt * 0.8, "quad", 0.125, r=0.01)
                f.add(inicio + k * passo_arp, n, 0.10 if estilo != "calmo" else 0.12)
            # --- melodia
            pos = 0.0
            for (nm, dur) in MELODIA[b]:
                if nm != "-":
                    m = midi(nm) + transp
                    if ps == 1 and estilo != "calmo":
                        m += 12 if (b % 4 in (0, 2) and dur >= 1) else 0
                    tipo_l = "quad" if estilo != "calmo" else "tri"
                    n = nota(m, dur * dt * 0.95, tipo_l, duty_lead, a=0.006, d=0.08, s=0.6, r=0.05)
                    f.add(inicio + pos, n, 0.30 if estilo != "calmo" else 0.4)
                pos += dur
            # --- bateria
            if estilo != "calmo":
                for beat in range(4):
                    if beat in (0, 2):
                        k_n = int(SR * 0.14)
                        kick = osc("seno", varredura(150, 45, 0.14), 0.14) * decai(k_n, 5)
                        f.add(inicio + beat, kick, 0.7)
                    else:
                        s_n = int(SR * 0.12)
                        f.add(inicio + beat, osc("ruido", 0, 0.12) * decai(s_n, 7), 0.35)
                    passos_hat = 4 if estilo == "chefe" else 2
                    for h in range(passos_hat):
                        h_n = int(SR * 0.03)
                        f.add(inicio + beat + h / passos_hat, osc("ruido", 0, 0.03) * decai(h_n, 5), 0.12)
    return f.final()


def jingle(notas, tipo="quad", duty=0.25, passo=0.14, final=0.6):
    partes = [nota(midi(n), passo, tipo, duty, r=0.02) for n in notas[:-1]]
    partes.append(nota(midi(notas[-1]), final, tipo, duty, r=0.3))
    return seq(*partes) * 0.6


def gerar_musicas():
    salvar_wav("musica_menu", compor(70, 0, 2, "calmo", 0.5), "musica", 0.8)
    salvar_wav("musica_fase1", compor(132, 0, 2, "normal", 0.25), "musica", 0.8)
    salvar_wav("musica_fase2", compor(120, 5, 2, "normal", 0.125), "musica", 0.8)
    salvar_wav("musica_fase3", compor(144, 7, 2, "normal", 0.5), "musica", 0.8)
    salvar_wav("musica_chefe", compor(172, 4, 2, "chefe", 0.125), "musica", 0.8)
    salvar_wav("jingle_gameover", jingle(["E4", "D4", "C4", "B3", "A3", "G#3", "A3"], "tri", passo=0.22, final=1.2), "musica")
    salvar_wav("jingle_vitoria", jingle(["C5", "E5", "G5", "C6", "G5", "C6", "E6", "G6", "C7"], "quad", 0.25, 0.13, 1.0), "musica")
    salvar_wav("jingle_fase", jingle(["A4", "C5", "E5", "A5", "E5", "A5", "C6"], "quad", 0.25, 0.12, 0.9), "musica")


def gerar_tudo():
    gerar_efeitos()
    gerar_musicas()

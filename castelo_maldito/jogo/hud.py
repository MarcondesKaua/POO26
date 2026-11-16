"""Interface do jogo: barras de vida, corações, armas, pontuação e barra do chefe."""
from . import recursos, ui
from .armas import ESPADAS, SUBARMAS
from .config import ALTURA, BRANCO, CINZA, LARGURA, NUM_FASES, OURO, VERDE, VERMELHO


def _icone(i):
    return recursos.quadros("sprites/itens")[0][i]


def _tempo(seg):
    return f"{int(seg) // 60:02d}:{int(seg) % 60:02d}"


def desenhar(tela):
    prog = tela.prog
    j = tela.jogador
    # --- painel superior esquerdo
    ui.retangulo(10, ALTURA - 82, 330, 72, (10, 6, 20, 190))
    ui.contorno(10, ALTURA - 82, 330, 72, (200, 170, 90, 255), 2)
    ui.texto("VIDA", 20, ALTURA - 34, OURO, 13)
    for k in range(prog.vida_max):
        cor = (214, 36, 60, 255) if k < prog.vida else (70, 30, 44, 255)
        ui.retangulo(70 + k * 21, ALTURA - 36, 18, 16, cor)
        if k < prog.vida:
            ui.retangulo(70 + k * 21, ALTURA - 24, 18, 4, (255, 120, 130, 255))
    ui.textura(_icone(0), 30, ALTURA - 62, 28, 28)
    ui.texto(f"x {prog.coracoes:02d}", 48, ALTURA - 68, BRANCO, 15)
    ui.texto(f"VIDAS x {prog.vidas}", 125, ALTURA - 68, BRANCO, 15)
    ui.texto(f"FASE {prog.fase + 1}/{NUM_FASES}", 245, ALTURA - 68, CINZA, 13)
    # --- armas (embaixo à esquerda)
    espada = ESPADAS[prog.arma_atual]
    ui.retangulo(10, 10, 230, 58, (10, 6, 20, 190))
    ui.contorno(10, 10, 230, 58, (200, 170, 90, 255), 2)
    ui.textura(_icone(espada["icone"]), 38, 40, 40, 40)
    ui.texto(espada["nome"], 64, 44, BRANCO, 13)
    ui.texto("[E] trocar", 64, 24, CINZA, 11)
    # --- sub-armas: 2 slots (o da mão fica destacado)
    ui.texto("SUB-ARMAS  [F] trocar", 250, 72, CINZA, 10)
    for k in range(2):
        x0 = 250 + k * 94
        nome = prog.subs[k] if k < len(prog.subs) else None
        ativo = nome is not None and k == prog.sub_atual
        ui.retangulo(x0, 10, 88, 58, (10, 6, 20, 190 if nome else 110))
        if ativo:
            ui.contorno(x0, 10, 88, 58, (200, 170, 90, 255), 3)
        else:
            ui.contorno(x0, 10, 88, 58, (110, 96, 66, 255) if nome else (70, 62, 50, 255), 2)
        if nome:
            sa = SUBARMAS[nome]
            ui.textura(_icone(sa["icone"]), x0 + 30, 42, 40, 40, BRANCO if ativo else (150, 150, 150, 255))
            ui.texto(f"-{sa['custo']}", x0 + 62, 26,
                     VERMELHO if prog.coracoes < sa["custo"] else (VERDE if ativo else CINZA), 14)
        else:
            ui.texto("vazio", x0 + 44, 34, (95, 88, 75, 255), 11, "center")
    # --- placar
    ui.retangulo(LARGURA - 230, ALTURA - 66, 220, 56, (10, 6, 20, 190))
    ui.contorno(LARGURA - 230, ALTURA - 66, 220, 56, (200, 170, 90, 255), 2)
    ui.texto(f"PONTOS {prog.pontos:07d}", LARGURA - 220, ALTURA - 36, OURO, 15)
    ui.texto(f"TEMPO {_tempo(prog.tempo)}", LARGURA - 220, ALTURA - 58, BRANCO, 13)
    # --- recarga do dash
    if j.dash_recarga > 0:
        pct = 1 - j.dash_recarga / 0.55
        ui.retangulo(450, 14, 80, 6, (40, 40, 60, 200))
        ui.retangulo(450, 14, 80 * pct, 6, (120, 200, 255, 255))
    # --- chefe
    ch = tela.chefe
    if ch is not None and not ch.morreu:
        w = 440
        x = (LARGURA - w) / 2
        if ch.etapa == 2 and ch.estado.startswith("f2"):
            # etapa 2: o chefe é invulnerável; a barra mostra o tempo que falta para sobreviver
            falta = ch.restante_f2 if ch.estado == "f2_roteiro" else ch.f2_total
            ui.texto_sombra(f"SOBREVIVA!   {int(falta + 0.99) // 60:02d}:{int(falta + 0.99) % 60:02d}",
                            LARGURA / 2, ALTURA - 28, (255, 190, 90, 255), 16, "center")
            ui.retangulo(x - 3, ALTURA - 52, w + 6, 18, (10, 6, 20, 230))
            ui.retangulo(x, ALTURA - 49, w * falta / ch.f2_total, 12, (230, 150, 40, 255))
            ui.contorno(x - 3, ALTURA - 52, w + 6, 18, (200, 170, 90, 255), 2)
        else:
            ui.texto_sombra(ch.nome, LARGURA / 2, ALTURA - 28, (255, 120, 140, 255), 16, "center")
            ui.retangulo(x - 3, ALTURA - 52, w + 6, 18, (10, 6, 20, 230))
            ui.retangulo(x, ALTURA - 49, w * max(0, ch.hp_atual) / ch.hp, 12, (190, 20, 50, 255))
            ui.contorno(x - 3, ALTURA - 52, w + 6, 18, (200, 170, 90, 255), 2)
    # --- corrida contra o Dodo
    if tela.corrida is not None:
        tela.corrida.desenhar_hud()
    # --- mensagem
    if tela.mensagem and tela.mensagem[1] > 0:
        a = min(255, int(tela.mensagem[1] * 400))
        ui.texto_sombra(tela.mensagem[0], LARGURA / 2, 120, (255, 240, 170, a), 20, "center")

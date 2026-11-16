"""Constantes globais do jogo."""
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")
ARQUIVO_BANCO = os.path.join(RAIZ, "ranking.db")

TITULO = "Castelo Maldito"
LARGURA = 1024
ALTURA = 576
TILE = 32

# --- física do jogador (valores por frame, a 60 FPS)
GRAVIDADE = 0.8
VEL_ANDAR = 4.6
FORCA_PULO = 15.5
VEL_QUEDA_MAX = 18.0
VEL_DASH = 11.5
TEMPO_COYOTE = 0.10
TEMPO_BUFFER_PULO = 0.12
TEMPO_DASH = 0.18
RECARGA_DASH = 0.55
TEMPO_ANIMACAO_CAMINHADA = 0.100  # troca de quadro a cada 100 ms (requisito do trabalho)
INVULNERAVEL_APOS_DANO = 1.3

# direções (atributo virado_para)
DIREITA = 0
ESQUERDA = 1

# --- índices dos quadros da folha do jogador (sprites/player.png)
Q_IDLE = 0
Q_ANDAR = (1, 2, 3, 4)
Q_PULO = 5
Q_QUEDA = 6
Q_ATQ_PREP = 7
Q_ATQ_GOLPE = 8
Q_ATQ_RECUP = 9
Q_DASH = 10
Q_FERIDO = 11
Q_MORTO = 12
Q_CAST = 13

# --- cores
BRANCO = (255, 255, 255, 255)
PRETO = (0, 0, 0, 255)
VERMELHO = (220, 40, 60, 255)
OURO = (255, 210, 80, 255)
CINZA = (170, 170, 190, 255)
VERDE = (110, 230, 140, 255)
AZUL = (110, 170, 255, 255)

# Fases: (id do tema, nome, música)
NUM_FASES = 5

# Fases: (tema dos tiles, tema do fundo, nome, música)
FASES = [
    ("cem", "cem", "Cemitério Sombrio", "musica_fase1"),
    ("salao", "salao", "Salão dos Vitrais Rubros", "musica_fase2"),
    ("torre", "torre", "Torre da Tempestade", "musica_fase3"),
    ("salao", "arena", "Trono do Conde Vorthal", "musica_chefe"),
    ("salao", "salao", "Corrida contra o Dodo", "musica_fase3"),
]

# --- fase de corrida (contra o Dodo)
VEL_CORRIDA_MULT = 1.4     # multiplicador da velocidade de andar do jogador na corrida

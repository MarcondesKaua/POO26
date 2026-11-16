# Castelo Maldito — Python Arcade + POO + Peewee

Jogo de plataforma 2D com tema Castlevania (Atividade Prática - Parte 2).

## Como rodar
```
pip install -r requirements.txt     # arcade 3.x e peewee
python main.py
```
Os assets (sprites, tiles, fundos, sons e músicas) já estão em `assets/` e foram gerados por código
(`python gerar_assets.py` regenera tudo; requer pillow e numpy).

## Controles
| Tecla | Ação |
|---|---|
| ← → / A D | andar |
| ESPAÇO / ↑ / W | pular (sem pulo duplo; segurar = pulo mais alto) |
| Z / J | espada |
| X / K | sub-arma (gasta corações) |
| C / L / SHIFT | dash |
| E / Q ou 1-4 | trocar de espada |
| P / ESC | pausar · M = som |
| R (menu) | ranking |

## Conteúdo
4 fases (Cemitério, Salão, Torre e a arena do chefe Conde Vorthal), 6 tipos de inimigo, 4 espadas, 4 sub-armas
(adaga, machado, água benta, bumerangue), checkpoints, vidas, itens, música e efeitos sonoros.

## Mapa dos requisitos do enunciado
| Requisito | Onde |
|---|---|
| PhysicsEnginePlatformer, gravidade, `can_jump()` | `jogo/tela_jogo.py`, `jogo/player.py` |
| Classe `Bloco(arcade.Sprite)` + `SpriteList` | `jogo/bloco.py`, `jogo/mapa.py` |
| `load_spritesheet()` + `get_texture_grid()` | `jogo/recursos.py` |
| Máquina de estados (Pulo → Parado → Andando, 100 ms, `virado_para`) | `Player.atualizar_animacao` |
| `BaseModel`, `Pontuacao`, `__str__` | `jogo/modelos.py` |
| `Pontuacao.create()` + `on_text`/`on_key_press` | `jogo/tela_gameover.py` |
| `TelaRanking` (consulta única no `__init__`, `enumerate`, `draw_text`) | `jogo/tela_ranking.py` |
| Atalho [R] | `jogo/tela_inicio.py` e `jogo/tela_gameover.py` |

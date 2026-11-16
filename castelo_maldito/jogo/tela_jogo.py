"""TelaJogo: a partida em si (física, combate, itens, câmera, HUD e fluxo entre fases)."""
import random

import arcade

from . import hud, recursos, ui
from .armas import ESPADAS, SUBARMAS
from .audio import audio
from .chefe import Chefe
from .config import (ALTURA, DIREITA, ESQUERDA, FASES, GRAVIDADE, LARGURA, TILE)
from .corpo import sinal, sobrepoe
from .corrida import Corrida
from .tela_debug import atalho_debug
from .efeitos import Efeitos
from .fases import construir_fase
from .inimigos import DROPS, FABRICA, Medusa, Zumbi
from .itens import Checkpoint, Item, Porta, Vela
from .player import Entrada, Player
from .projeteis import Agua, Bumerangue, Chama, Pilar, Projetil

K = arcade.key


class TelaJogo(arcade.View):
    def __init__(self, indice_fase, progresso, fase2=False):
        super().__init__()
        self.indice = indice_fase
        self.prog = progresso
        self.prog.fase = indice_fase
        self.audio = audio
        self.mapa = construir_fase(indice_fase)
        self.blocos, self.espinhos, self.deco = self.mapa.construir()
        self.entrada = Entrada()
        self.efeitos = Efeitos()
        self.camera = arcade.Camera2D()

        cx, cy = self.mapa.inicio
        self.ponto_respawn = (cx * TILE + TILE / 2, cy * TILE + 37)
        self.jogador = Player(*self.ponto_respawn, self.prog, self.entrada)
        self.jogador.jogo = self
        self.lista_jogador = arcade.SpriteList()
        self.lista_jogador.append(self.jogador)
        self.fisica = arcade.PhysicsEnginePlatformer(self.jogador, walls=self.blocos, gravity_constant=GRAVIDADE)
        self.jogador.vincular_fisica(self.fisica)
        self.prog.vida = self.prog.vida_max

        self.inimigos = arcade.SpriteList()
        self.proj_jogador = arcade.SpriteList()
        self.projeteis_inimigos = arcade.SpriteList()
        self.chamas = arcade.SpriteList()
        self.itens = arcade.SpriteList()
        self.velas = arcade.SpriteList()
        self.checkpoints = arcade.SpriteList()
        self.portas = arcade.SpriteList()
        self.tochas = []
        self.chefe = None
        self.spawns = []
        self.timers_zona = {}
        self.perigos = []         # perigos desenhados por código (ex.: a cruz de fogo do chefe): .ia/.desenhar/.caixas
        self.fase2 = fase2        # True depois que o chefe zera a vida: a luta passa a ser "sobreviver"
        self._montar_entidades()

        self.cam_x = LARGURA / 2
        self.cam_olhar = 0.0
        self.shake = 0.0
        self.tempo = 0.0
        self.t_banner = 3.0
        self.pausado = False
        self.mensagem = None
        self.saindo = None        # ("proxima", t) | ("vitoria", t) | ("gameover", t)
        self.chefe_caindo = False
        self.jogador.mult_vel = self.mapa.mult_vel
        self.corrida = Corrida(self) if self.mapa.corrida else None   # fase de corrida contra o Dodo

    # ------------------------------------------------------------------ montagem
    def _montar_entidades(self):
        m = self.mapa
        for c, r, drop in m.velas:
            v = Vela(c * TILE + TILE / 2, r * TILE, drop)
            self.velas.append(v)
        for c, r in m.checkpoints:
            self.checkpoints.append(Checkpoint(c * TILE + TILE / 2, r * TILE))
        if m.porta:
            self.portas.append(Porta(m.porta[0] * TILE + TILE / 2, m.porta[1] * TILE))
        for tipo, c, r in m.itens:
            self.itens.append(Item(tipo, c * TILE + TILE / 2, r * TILE + 16, permanente=True))
        for tipo, c, r in m.inimigos:
            self.spawns.append({"tipo": tipo, "x": c * TILE + TILE / 2, "y": r * TILE, "estado": "espera", "ref": None})
        for x, y in m.tochas:
            self.tochas.append((x, y))
        self.tex_tocha = recursos.quadros("sprites/tocha")[0]
        self._criar_chefe()

    def _criar_chefe(self):
        if self.mapa.chefe:
            c, r = self.mapa.chefe
            self.chefe = Chefe(c * TILE + TILE / 2, r * TILE, etapa=2 if self.fase2 else 1)
            self.inimigos.append(self.chefe)

    def on_show_view(self):
        self.window.background_color = (0, 0, 0, 255)
        self.audio.musica(self.mapa.musica)
        self.entrada.limpar()

    # ------------------------------------------------------------------ utilidades públicas (usadas por entidades)
    def tremer(self, t):
        self.shake = max(self.shake, t)

    def explodir(self, x, y):
        self.efeitos.faiscas(x, y, (255, 170, 40, 255), 14, 5, 0.6)
        self.efeitos.faiscas(x, y, (255, 240, 160, 255), 6, 3, 0.4)
        self.audio.tocar("explosao", 0.6)

    def criar_chama(self, x, y):
        topo = self.mapa.topo_do_chao(x, y + 20)
        if topo is not None:
            self.chamas.append(Chama(x, topo))
            self.audio.tocar("fogo", 0.6)

    def lancar_sub(self, j, nome):
        s = j.sinal_dir
        x, y = j.center_x + s * 20, j.center_y + 12
        if nome == "adaga":
            p = Projetil("sprites/adaga", x, y, 12 * s, 0, dano=2, periodo=1.0, vida=1.5)
        elif nome == "machado":
            p = Projetil("sprites/machado", x, y, 4.5 * s, 12, dano=4, grav=0.55, atravessa=True, periodo=0.06, vida=3.0)
        elif nome == "agua":
            p = Agua(x, y, j.virado_para)
        else:
            if any(isinstance(q, Bumerangue) for q in self.proj_jogador):
                self.prog.coracoes += SUBARMAS[nome]["custo"]   # só um no ar: devolve o custo
                return
            p = Bumerangue(x, y, j.virado_para, j)
        self.proj_jogador.append(p)
        self.audio.tocar("arremesso")

    def avisar(self, texto):
        self.mensagem = [texto, 2.6]

    # ------------------------------------------------------------------ entrada
    def on_key_press(self, tecla, mods):
        if atalho_debug(self, tecla, mods):     # Alt+L: menu de testes
            return
        if tecla in (K.P, K.ESCAPE):
            self.pausado = not self.pausado
            self.entrada.limpar()
            self.audio.tocar("menu_ok")
            return
        if tecla == K.M:
            self.audio.alternar_mudo()
            return
        if self.pausado:
            if tecla == K.BACKSPACE:
                from .tela_inicio import TelaInicial
                self.audio.parar_musica()
                self.window.show_view(TelaInicial())
            return
        if tecla in (K.E, K.Q):
            self._trocar_arma(1 if tecla == K.E else -1)
            return
        if tecla == K.F:
            self._trocar_sub()
            return
        if tecla in (K.KEY_1, K.KEY_2, K.KEY_3, K.KEY_4):
            i = {K.KEY_1: 0, K.KEY_2: 1, K.KEY_3: 2, K.KEY_4: 3}[tecla]
            if i in self.prog.armas:
                self.prog.arma_atual = i
                self.audio.tocar("troca_arma")
            return
        self.entrada.pressionar(tecla)

    def on_key_release(self, tecla, mods):
        self.entrada.soltar(tecla)

    def on_mouse_press(self, x, y, botao, mods):
        """Botão esquerdo = espada, botão direito = sub-arma."""
        if self.pausado:
            return
        self.entrada.clicar(botao)

    def _trocar_arma(self, passo):
        lista = sorted(self.prog.armas)
        if len(lista) > 1:
            i = (lista.index(self.prog.arma_atual) + passo) % len(lista)
            self.prog.arma_atual = lista[i]
            self.audio.tocar("troca_arma")

    def _trocar_sub(self):
        if self.prog.trocar_sub():
            self.audio.tocar("troca_arma")
            self.avisar(f"Sub-arma na mão: {SUBARMAS[self.prog.sub]['nome']}")

    # ------------------------------------------------------------------ atualização
    def on_update(self, dt):
        if self.pausado:
            return
        dt = min(dt, 1 / 30)
        if self.saindo:
            self._atualizar_saida(dt)
        self.tempo += dt
        self.t_banner = max(0.0, self.t_banner - dt)
        if self.mensagem:
            self.mensagem[1] -= dt
        if not self.saindo or self.saindo[0] != "gameover":
            self.prog.tempo += dt
        j = self.jogador
        if self.corrida:
            self.corrida.atualizar(dt)
        j.update(dt)
        self.fisica.update()
        self._limites(j)
        self._queda_e_espinhos(j)
        self._ativar_spawns(dt)
        self._zonas(dt)
        self._atualizar_entidades(dt)
        self._combate(dt)
        self._morte(dt)
        self._camera(dt)
        self.efeitos.atualizar(dt)

    def _limites(self, j):
        if j.center_x < 20:
            j.center_x = 20
        if j.center_x > self.mapa.largura_px - 20:
            j.center_x = self.mapa.largura_px - 20

    def _queda_e_espinhos(self, j):
        if j.morto:
            return
        if j.center_y < -80:
            if self.corrida:                 # corrida: não morre, volta ao último chão firme
                self.corrida.queda(j)
                return
            j.prog.vida = 0
            self.audio.tocar("dano")
            j.morrer()
            j.tempo_morto = 0.9
            return
        for e in self.espinhos:
            if sobrepoe(j.caixa, e.caixa):
                if j.receber_dano(2, e.center_x):
                    j.change_y = 9.0
                break

    # ------------------------------------------------------------------ spawns
    def _ativar_spawns(self, dt):
        px = self.jogador.center_x
        for d in self.spawns:
            if d["estado"] == "espera" and abs(d["x"] - px) < 640:
                e = FABRICA[d["tipo"]](d["x"], d["y"])
                e.spawn = d
                e.mapa = self.mapa
                d["ref"], d["estado"] = e, "ativo"
                self.inimigos.append(e)
            elif d["estado"] == "ativo" and d["ref"] is not None and abs(d["ref"].center_x - px) > 1100:
                d["ref"].remove_from_sprite_lists()
                d["ref"], d["estado"] = None, "espera"

    def _zonas(self, dt):
        px = self.jogador.center_x
        for i, (tipo, c0, c1) in enumerate(self.mapa.zonas):
            if not (c0 * TILE <= px <= c1 * TILE):
                continue
            t = self.timers_zona.get(i, 1.0) - dt
            if t > 0:
                self.timers_zona[i] = t
                continue
            if tipo == "zumbi":
                if sum(isinstance(e, Zumbi) for e in self.inimigos) < 3:
                    x = px + random.choice((-1, 1)) * random.uniform(520, 600)
                    y = self.mapa.topo_do_chao(x, ALTURA)
                    if y is not None and 0 < x < self.mapa.largura_px:
                        z = Zumbi(x, y)
                        z.virar_para(px)
                        z.efemero = True
                        self.inimigos.append(z)
                self.timers_zona[i] = random.uniform(1.4, 2.8)
            elif tipo == "medusa":
                if sum(isinstance(e, Medusa) for e in self.inimigos) < 3:
                    m = Medusa(self.cam_x + LARGURA / 2 + 40, random.uniform(150, 400))
                    m.efemero = True
                    self.inimigos.append(m)
                self.timers_zona[i] = random.uniform(2.0, 3.4)

    # ------------------------------------------------------------------ entidades
    def _atualizar_entidades(self, dt):
        px = self.jogador.center_x
        for e in list(self.inimigos):
            if abs(e.center_x - px) > 1000 and not isinstance(e, Chefe):
                if getattr(e, "efemero", False):
                    e.remove_from_sprite_lists()
                continue
            e.ia(dt, self)
            if isinstance(e, Chefe) and e.morreu:
                e.remove_from_sprite_lists()
                self._chefe_derrotado()
        for lista in (self.proj_jogador, self.projeteis_inimigos, self.chamas, self.itens):
            for p in list(lista):
                p.ia(dt, self)
                if p.morreu:
                    p.remove_from_sprite_lists()
        for pg in list(self.perigos):
            pg.ia(dt, self)
            if pg.morreu:
                self.perigos.remove(pg)
        for lista in (self.velas, self.checkpoints, self.portas):
            for s in lista:
                s.ia(dt, self)
        if self.mensagem and self.mensagem[1] <= 0:
            self.mensagem = None

    # ------------------------------------------------------------------ combate
    def _atingir(self, alvo, dano, origem_x, empurrao):
        if getattr(alvo, "morreu", False):
            return
        if isinstance(alvo, Vela):
            self._quebrar_vela(alvo)
            return
        res = alvo.receber_dano(dano, origem_x, empurrao)
        if res == "bloqueado":
            self.audio.tocar("vidro", 0.5)
            self.efeitos.faiscas(alvo.center_x + 16 * sinal(origem_x - alvo.center_x), alvo.center_y,
                                 (220, 230, 255, 255), 5, 3, 0.3)
            return
        self.audio.tocar("acerto_forte" if dano >= 4 else "acerto", 0.8)
        self.efeitos.faiscas(alvo.center_x, alvo.center_y, (255, 255, 255, 255), 5, 3, 0.3)
        if self.prog.arma_atual == 3 and dano == ESPADAS[3]["dano"]:
            self.jogador.acertos_vampiro += 1
            if self.jogador.acertos_vampiro % 5 == 0:
                self.prog.vida = min(self.prog.vida_max, self.prog.vida + 1)
        if res == "morto":
            if isinstance(alvo, Chefe):
                self._chefe_cai()
            else:
                self._matar(alvo)

    def _quebrar_vela(self, v):
        v.morreu = True
        v.remove_from_sprite_lists()
        self.audio.tocar("vela")
        self.efeitos.faiscas(v.center_x, v.center_y, (255, 200, 80, 255), 8, 3, 0.5)
        drop = v.drop or random.choice(["coracao", "coracao", "coracao_g", "moeda", "carne"])
        self.itens.append(Item(drop, v.center_x, v.center_y, vy=6))

    def _matar(self, e):
        self.prog.pontos += e.pontos
        self.prog.abates += 1
        self.audio.tocar("inimigo_morre", 0.8)
        self.efeitos.faiscas(e.center_x, e.center_y, (230, 200, 255, 255), 12, 5, 0.6)
        self.efeitos.texto(e.center_x, e.center_y + 30, f"+{e.pontos}")
        d = getattr(e, "spawn", None)
        if d:
            d["estado"], d["ref"] = "morto", None
        nome = type(e).__name__.lower()
        if random.random() < DROPS.get(nome, 0.2):
            vida_baixa = self.prog.vida <= 4
            tipo = "carne" if (vida_baixa and random.random() < 0.5) else random.choice(
                ["coracao", "coracao", "coracao", "coracao_g", "moeda"])
            self.itens.append(Item(tipo, e.center_x, e.center_y + 10, vy=6))
        e.remove_from_sprite_lists()

    def _chefe_cai(self):
        if self.chefe_caindo:
            return
        self.chefe_caindo = True
        self.audio.parar_musica()
        self.audio.tocar("chefe_morre")
        self.tremer(1.5)
        self.projeteis_inimigos.clear()
        self.perigos.clear()

    def _combate(self, dt):
        j = self.jogador
        # espada
        caixa = j.caixa_ataque()
        if caixa:
            acertos = j.ataque["acertos"]
            dano, emp = j.arma["dano"], j.arma["empurrao"]
            for alvo in list(self.inimigos) + list(self.velas):
                if id(alvo) in acertos:
                    continue
                if sobrepoe(caixa, alvo.caixa):
                    acertos.add(id(alvo))
                    self._atingir(alvo, dano, j.center_x, emp)
        # sub-armas
        for p in list(self.proj_jogador):
            for alvo in list(self.inimigos) + list(self.velas):
                if id(alvo) in p.atingidos:
                    continue
                if sobrepoe(p.caixa, alvo.caixa):
                    p.atingidos.add(id(alvo))
                    self._atingir(alvo, p.dano, p.center_x, 0)
                    p.ao_acertar(self)
                    if p.morreu:
                        break
        # chamas
        for c in self.chamas:
            for alvo in list(self.inimigos) + list(self.velas):
                if sobrepoe(c.caixa, alvo.caixa):
                    ult = c.recarga.get(id(alvo), -1)
                    if self.tempo - ult > 0.4:
                        c.recarga[id(alvo)] = self.tempo
                        self._atingir(alvo, 2, c.center_x, 0)
        # inimigos x jogador
        if not j.morto:
            for e in self.inimigos:
                if isinstance(e, Chefe) and e.sem_contato:
                    continue
                if sobrepoe(j.caixa, e.caixa):
                    j.receber_dano(e.dano_contato, e.center_x)
                gc = getattr(e, "caixa_golpe", None)
                gc = gc() if callable(gc) else gc
                if gc and sobrepoe(j.caixa, gc):
                    j.receber_dano(e.dano_contato + 1, e.center_x)
            for p in self.projeteis_inimigos:
                if not getattr(p, "perigoso", True):
                    continue
                if sobrepoe(j.caixa, p.caixa):
                    if j.receber_dano(p.dano, p.center_x) and not p.atravessa:
                        p.morreu = True
            for pg in self.perigos:     # cruz de fogo etc.
                if pg.ativo and any(sobrepoe(j.caixa, cx) for cx in pg.caixas):
                    j.receber_dano(pg.dano, pg.origem_x)
        # itens, checkpoints, porta
        if not j.morto:
            for it in list(self.itens):
                if sobrepoe(j.caixa, it.caixa):
                    if not it.travado:
                        self._coletar(it)
                elif it.travado:
                    it.travado = False   # o jogador saiu de cima: agora pode pegar de volta
            for c in self.checkpoints:
                if not c.ativo and sobrepoe(j.caixa, c.caixa):
                    c.ativar()
                    self.ponto_respawn = (c.center_x, c.bottom + 37 + 2)
                    self.prog.vida = min(self.prog.vida_max, self.prog.vida + 4)
                    self.audio.tocar("checkpoint")
                    self.avisar("Checkpoint!")
            if not self.saindo:
                for p in self.portas:
                    if sobrepoe(j.caixa, p.caixa):
                        self._concluir_fase()

    def _coletar(self, it):
        t, p = it.tipo, self.prog
        if t == "coracao":
            p.coracoes = min(99, p.coracoes + 1)
            self.audio.tocar("coracao")
        elif t == "coracao_g":
            p.coracoes = min(99, p.coracoes + 5)
            self.audio.tocar("coracao")
        elif t == "carne":
            p.vida = min(p.vida_max, p.vida + 5)
            self.audio.tocar("comida")
        elif t == "moeda":
            p.pontos += 100
            self.audio.tocar("moeda")
        elif t == "bolsa":
            p.pontos += 500
            self.audio.tocar("moeda")
            self.avisar("Bolsa de ouro! +500")
        elif t == "calice":
            p.pontos += 1000
            self.audio.tocar("item_forte")
            self.avisar("Cálice sagrado! +1000")
        elif t == "cruz":
            p.vidas += 1
            self.audio.tocar("item_forte")
            self.avisar("Vida extra!")
        elif t in SUBARMAS:
            if t in p.subs:                      # já tem essa: não gasta o item
                if not it.avisado:
                    it.avisado = True
                    self.avisar(f"Você já tem: {SUBARMAS[t]['nome']}")
                return
            largada = p.pegar_sub(t)
            self.audio.tocar("troca_arma")
            if largada:                          # slots cheios: a da mão cai no chão
                j = self.jogador
                caida = Item(largada, j.center_x, j.center_y, vy=7, permanente=True)
                caida.soltado = True
                caida.travado = True
                self.itens.append(caida)
                self.avisar(f"{SUBARMAS[t]['nome']} equipada - {SUBARMAS[largada]['nome']} caiu no chão")
            elif len(p.subs) == 1:
                self.avisar(f"Sub-arma: {SUBARMAS[t]['nome']}  [botão dir./X] usar")
            else:
                self.avisar(f"{SUBARMAS[t]['nome']} equipada  [F] troca de sub-arma")
        elif t.startswith("arma"):
            i = int(t[-1])
            if i not in p.armas:
                p.armas.append(i)
            p.arma_atual = i
            self.audio.tocar("item_forte")
            self.avisar(f"{ESPADAS[i]['nome']} conquistada!  [E] troca de arma")
        self.efeitos.faiscas(it.center_x, it.center_y, (255, 240, 160, 255), 6, 3, 0.4)
        it.remove_from_sprite_lists()

    # ------------------------------------------------------------------ morte e fluxo
    def _morte(self, dt):
        j = self.jogador
        if j.morto and j.tempo_morto > 1.6 and not self.saindo:
            self.prog.vidas -= 1
            self.prog.mortes += 1
            if self.prog.vidas <= 0:
                self.saindo = ("gameover", 1.2)
                self.audio.musica("jingle_gameover", repetir=False)
            else:
                self._renascer()

    def _renascer(self):
        j = self.jogador
        j.reviver(*self.ponto_respawn)
        self.projeteis_inimigos.clear()
        self.proj_jogador.clear()
        self.chamas.clear()
        self.perigos.clear()
        for e in list(self.inimigos):
            e.remove_from_sprite_lists()
        for d in self.spawns:
            if d["estado"] == "ativo":
                d["estado"], d["ref"] = "espera", None
        self.chefe = None
        self.chefe_caindo = False
        self._criar_chefe()
        if self.chefe:
            self.audio.musica(self.mapa.musica)
            self._recriar_velas()   # arena do chefe: os castiçais voltam, para dar para reabastecer corações/vida
        if self.corrida:
            self.corrida.reiniciar()

    def _chefe_derrotado(self):
        """Depois do chefe ainda há a corrida contra o Dodo; se não houver mais fases, é a vitória final."""
        if self.indice + 1 < len(FASES):
            if self.saindo:
                return
            self.prog.pontos += 5000
            self.chefe = None
            self.saindo = ("proxima", 3.2)
            self.audio.musica("jingle_vitoria", repetir=False)
        else:
            self._vitoria()

    def corrida_vencida(self, premio):
        """O jogador cruzou a linha de chegada antes do Dodo."""
        self._vitoria(premio)

    def _recriar_velas(self):
        """Reconstrói todas as velas do mapa (usado ao renascer na luta contra o chefe)."""
        self.velas.clear()
        for c, r, drop in self.mapa.velas:
            self.velas.append(Vela(c * TILE + TILE / 2, r * TILE, drop))

    def _concluir_fase(self):
        self.saindo = ("proxima", 1.8)
        self.prog.pontos += 500
        self.audio.musica("jingle_fase", repetir=False)

    def _vitoria(self, pontos=5000):
        if self.saindo:
            return
        self.prog.pontos += pontos + self.prog.bonus_final()
        self.prog.venceu = True
        self.chefe = None
        self.saindo = ("vitoria", 3.2)
        self.audio.musica("jingle_vitoria", repetir=False)

    def _atualizar_saida(self, dt):
        tipo, t = self.saindo
        t -= dt
        self.saindo = (tipo, t)
        if t > 0:
            return
        from .tela_gameover import TelaGameOver
        from .tela_transicao import TelaTransicao
        if tipo == "proxima":
            self.window.show_view(TelaTransicao(self.indice + 1, self.prog))
        else:
            self.window.show_view(TelaGameOver(self.prog))

    # ------------------------------------------------------------------ câmera
    def _camera(self, dt):
        j = self.jogador
        alvo_olhar = 60 * j.sinal_dir
        self.cam_olhar += (alvo_olhar - self.cam_olhar) * min(1.0, dt * 3)
        alvo = j.center_x + self.cam_olhar
        self.cam_x += (alvo - self.cam_x) * min(1.0, dt * 8)
        meio = LARGURA / 2
        self.cam_x = max(meio, min(self.mapa.largura_px - meio, self.cam_x))
        self.shake = max(0.0, self.shake - dt)

    # ------------------------------------------------------------------ desenho
    def _fundo(self):
        esq = self.cam_x - LARGURA / 2
        tema = self.mapa.tema_fundo
        for i, f in enumerate((0.05, 0.22, 0.5)):
            tex = recursos.textura("bg", f"{tema}_{i}.png")
            off = -((esq * f) % LARGURA)
            ui.textura(tex, off + LARGURA / 2, ALTURA / 2, LARGURA, ALTURA)
            ui.textura(tex, off + LARGURA * 1.5, ALTURA / 2, LARGURA, ALTURA)

    def on_draw(self):
        self.clear()
        ui.camera_padrao()
        self._fundo()
        sx = random.uniform(-1, 1) * self.shake * 12 if self.shake > 0 else 0
        sy = random.uniform(-1, 1) * self.shake * 12 if self.shake > 0 else 0
        self.camera.position = (self.cam_x + sx, ALTURA / 2 + sy)
        self.camera.use()
        self.deco.draw()
        fr = int(self.tempo * 6) % 2
        for x, y in self.tochas:
            ui.textura(self.tex_tocha[fr], x, y + 26)
        self.blocos.draw()
        self.espinhos.draw()
        self.portas.draw()
        self.checkpoints.draw()
        self.velas.draw()
        self.itens.draw()
        self.chamas.draw()
        self.inimigos.draw()
        for p in self.projeteis_inimigos:
            if isinstance(p, Pilar) and not p.perigoso:
                ui.retangulo(p.center_x - 3, p.center_y - 100, 6, 200,
                             (255, 40, 40, 90 + int(80 * (self.tempo * 10 % 1))))
        self.projeteis_inimigos.draw()
        for pg in self.perigos:
            pg.desenhar()
        self.proj_jogador.draw()
        if self.corrida:
            self.corrida.desenhar_mundo()     # linha de chegada e o Dodo (atrás do jogador)
        self.lista_jogador.draw()
        self._desenhar_arco()
        self.efeitos.desenhar()
        ui.camera_padrao()
        vinheta = recursos.textura("ui", "vinheta.png")
        ui.textura(vinheta, LARGURA / 2, ALTURA / 2, LARGURA, ALTURA)
        hud.desenhar(self)
        self._banner()
        if self.saindo and self.saindo[0] in ("proxima", "vitoria", "gameover"):
            a = int(min(255, (1 - self.saindo[1] / 1.5) * 255)) if self.saindo[1] < 1.5 else 0
            ui.retangulo(0, 0, LARGURA, ALTURA, (0, 0, 0, max(0, a)))
        if self.pausado:
            ui.fundo_escuro(190)
            ui.texto_sombra("PAUSADO", LARGURA / 2, ALTURA / 2 + 40, (255, 230, 150, 255), 40, "center")
            ui.texto("[P] continuar    [M] som    [BACKSPACE] menu principal", LARGURA / 2, ALTURA / 2 - 10,
                     (230, 230, 240, 255), 16, "center")

    def _desenhar_arco(self):
        j = self.jogador
        if j.ataque and j.ataque["fase"] in ("golpe", "recup"):
            q = recursos.quadros("sprites/golpe")
            lista = q[0] if j.virado_para == DIREITA else q[1]
            i = 1 if j.ataque["fase"] == "golpe" else 2
            if j.ataque["fase"] == "golpe" and j.ataque["t"] < j.arma["golpe"] / 2:
                i = 0
            x, y = j.posicao_arco()
            esc = j.arma["alcance"] / 74
            ui.textura(lista[i], x, y, lista[i].width * esc, lista[i].height * esc, j.arma["cor"])

    def _banner(self):
        if self.t_banner <= 0:
            return
        a = int(255 * min(1.0, self.t_banner))
        ui.texto_sombra(f"FASE {self.indice + 1}", LARGURA / 2, ALTURA / 2 + 60, (255, 230, 150, a), 34, "center")
        ui.texto_sombra(self.mapa.nome, LARGURA / 2, ALTURA / 2 + 15, (240, 240, 250, a), 22, "center")

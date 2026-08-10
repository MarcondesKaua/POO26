import arcade
import random
import time

DIMENSAO_X = 800
DIMENSAO_Y = 600
TITULO_SISTEMA = "Coletor do Tesouro - POO"

# ---------------------------------------------------------
# NOVO: constante de gravidade e força do pulo.
# Mude GRAVIDADE aqui para deixar o personagem mais "leve" ou mais "pesado".
# ---------------------------------------------------------
GRAVIDADE = 0.5
FORCA_PULO = 16


class ItemMoedaPadrao(arcade.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__("moeda.png", scale=0.6)
        self.center_x = pos_x
        self.center_y = pos_y


class ItemMoedaEspecial(arcade.Sprite):
    def __init__(self, pos_x, pos_y, vel):
        super().__init__("moeda.png", scale=0.8)
        self.center_x = pos_x
        self.center_y = pos_y
        self.change_x = vel
        self.change_y = vel

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.right > DIMENSAO_X or self.left < 0:
            self.change_x *= -1
        if self.top > DIMENSAO_Y or self.bottom < 0:
            self.change_y *= -1


class ObstaculoRegular(arcade.Sprite):
    def __init__(self, pos_x, pos_y, vel):
        super().__init__("InimigoDireita.png", scale=1)
        self.center_x = pos_x
        self.center_y = pos_y
        self.change_x = vel
        self.change_y = vel

        self.texture_right = self.texture
        self.texture_left = arcade.load_texture("InimigoEsquerda.png")

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.right >= DIMENSAO_X:
            self.right = DIMENSAO_X
            self.change_x *= -1
            self.texture = self.texture_left
        elif self.left <= 0:
            self.left = 0
            self.change_x *= -1
            self.texture = self.texture_right

        if self.top > DIMENSAO_Y:
            self.top = DIMENSAO_Y
            self.change_y *= -1

        if self.bottom < 0:
            self.bottom = 0
            self.change_y *= -1


class ObstaculoPerseguidor(arcade.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__("InimigoDireita.png", scale=1.2)
        self.center_x = pos_x
        self.center_y = pos_y
        self.velocidade_passo = 1.2

        self.texture_right = self.texture
        self.texture_left = arcade.load_texture("InimigoEsquerda.png")

    def perseguir_alvo(self, alvo_x, alvo_y):
        if self.center_x < alvo_x:
            self.center_x += self.velocidade_passo
            self.texture = self.texture_right
        elif self.center_x > alvo_x:
            self.center_x -= self.velocidade_passo
            self.texture = self.texture_left

        if self.center_y < alvo_y:
            self.center_y += self.velocidade_passo
        elif self.center_y > alvo_y:
            self.center_y -= self.velocidade_passo

    def relocar_aleatoriamente(self):
        self.center_x = random.randint(60, DIMENSAO_X - 60)
        self.center_y = random.randint(60, DIMENSAO_Y - 60)


# ---------------------------------------------------------
# NOVO: classe Bloco, representa cada peça do chão/plataforma.
# ---------------------------------------------------------
class Bloco(arcade.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__("bloco.png", scale=0.5)
        self.center_x = pos_x
        self.center_y = pos_y


class PersonagemHeroi(arcade.Sprite):
    def __init__(self):
        super().__init__("direita.png", scale=0.3)
        self.skin_direita = arcade.load_texture("direita.png")
        self.skin_esquerda = arcade.load_texture("esquerda.png")
        self.skin_cima = arcade.load_texture("cima.png")
        self.skin_baixo = arcade.load_texture("baixo.png")

        self.em_iframe = False
        self.tempo_iframe = 0.0

    def update(self, delta_time):
        # ---------------------------------------------------------
        # ATENÇÃO: o movimento no eixo Y (queda/pulo) agora é
        # inteiramente controlado pelo arcade.PhysicsEnginePlatformer
        # (ele soma a gravidade e resolve colisões com os blocos).
        # Por isso NÃO somamos mais self.change_y aqui, só o eixo X.
        # ---------------------------------------------------------
        self.center_x += self.change_x

        if self.em_iframe:
            self.tempo_iframe -= delta_time
            if self.tempo_iframe <= 0:
                self.em_iframe = False

        if self.change_x > 0:
            self.texture = self.skin_direita
        elif self.change_x < 0:
            self.texture = self.skin_esquerda
        elif self.change_y > 0:
            self.texture = self.skin_cima
        elif self.change_y < 0:
            self.texture = self.skin_baixo

        # Bordas laterais da tela
        if self.right > DIMENSAO_X:
            self.change_x = 0
            self.right = DIMENSAO_X
        if self.left < 0:
            self.change_x = 0
            self.left = 0

        # O chão é resolvido pelos Blocos + motor de física (por isso não
        # travamos mais o self.bottom aqui). Mas o TOPO da tela não tem
        # nenhum bloco/teto físico, então ainda precisamos travar manualmente
        # para o personagem não sair voando pra fora da tela num pulo forte.
        if self.top > DIMENSAO_Y:
            self.top = DIMENSAO_Y
            self.change_y = 0


class TelaMenuPrincipal(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()
        arcade.draw_text("COLETOR DE TESOUROS", DIMENSAO_X / 2, 420, arcade.color.WHITE, 30, anchor_x="center")
        arcade.draw_text("[J] Jogar Partida", DIMENSAO_X / 2, 320, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("[I] Instruções de Jogo", DIMENSAO_X / 2, 270, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("[S] Sobre os Desenvolvedores", DIMENSAO_X / 2, 220, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("[ESC] Sair do Jogo", DIMENSAO_X / 2, 170, arcade.color.WHITE, 18, anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.J:
            self.window.show_view(TelaPartidaAtiva())
        elif tecla == arcade.key.I:
            self.window.show_view(TelaTutorial())
        elif tecla == arcade.key.S:
            self.window.show_view(TelaSobre())
        elif tecla == arcade.key.ESCAPE:
            arcade.close_window()


class TelaTutorial(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_GREEN)

    def on_draw(self):
        self.clear()
        arcade.draw_text("INSTRUÇÕES & CONTROLES", DIMENSAO_X / 2, 480, arcade.color.GOLD, 26, anchor_x="center")
        arcade.draw_text("• Movimente-se usando as SETAS ou teclas WASD (esquerda/direita).", DIMENSAO_X / 2, 380, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("• Pressione [ESPAÇO] ou [CIMA] para pular.", DIMENSAO_X / 2, 340, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("• Colete todas as moedas simples (+1pt) e especiais (+5pts).", DIMENSAO_X / 2, 300, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("• EVITE OS FANTASMAS: se sua pontuação ficar menor que 0, é GAME OVER!", DIMENSAO_X / 2, 260, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("• Colete todas as moedas para vencer a partida.", DIMENSAO_X / 2, 220, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("Pressione [M] ou [ESC] para retornar ao Menu", DIMENSAO_X / 2, 120, arcade.color.LIGHT_GRAY, 15, anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla in (arcade.key.M, arcade.key.ESCAPE):
            self.window.show_view(TelaMenuPrincipal())


class TelaSobre(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.lista_icones = arcade.SpriteList()

        self.corleones_icon = arcade.Sprite("Corleone.png", scale=0.08)
        self.corleones_icon.center_x = DIMENSAO_X / 2 - 140
        self.corleones_icon.center_y = 308
        self.lista_icones.append(self.corleones_icon)

        self.santos_icon = arcade.Sprite("Santos.png", scale=0.08)
        self.santos_icon.center_x = DIMENSAO_X / 2 - 170
        self.santos_icon.center_y = 258
        self.lista_icones.append(self.santos_icon)

    def on_draw(self):
        self.clear()
        arcade.draw_text("SOBRE O JOGO", DIMENSAO_X / 2, 450, arcade.color.GOLD, 30, anchor_x="center")
        arcade.draw_text("Desenvolvido por:", DIMENSAO_X / 2, 360, arcade.color.WHITE, 20, anchor_x="center")

        self.lista_icones.draw()

        arcade.draw_text("• João Marcos", DIMENSAO_X / 2 + 20, 300, arcade.color.LIGHT_BLUE, 18, anchor_x="center")
        arcade.draw_text("• João Pedro dos Santos", DIMENSAO_X / 2 + 20, 250, arcade.color.LIGHT_BLUE, 18, anchor_x="center")
        arcade.draw_text("Projeto acadêmico focado em Programação Orientada a Objetos (POO).", DIMENSAO_X / 2, 180, arcade.color.WHITE, 14, anchor_x="center")
        arcade.draw_text("Pressione [M] ou [ESC] para retornar ao Menu", DIMENSAO_X / 2, 100, arcade.color.LIGHT_GRAY, 15, anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla in (arcade.key.M, arcade.key.ESCAPE):
            self.window.show_view(TelaMenuPrincipal())


class TelaGameOver(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_text("GAME OVER!", DIMENSAO_X / 2, 380, arcade.color.RED, 36, anchor_x="center")
        arcade.draw_text("Você ficou devendo pontos para os fantasmas...", DIMENSAO_X / 2, 300, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("Pressione [M] para o Menu ou [ESC] para Sair", DIMENSAO_X / 2, 180, arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.M:
            self.window.show_view(TelaMenuPrincipal())
        elif tecla == arcade.key.ESCAPE:
            arcade.close_window()


class TelaFinalizacao(arcade.View):
    def __init__(self, pontuacao_obtida, tempo_gasto, sofreu_dano):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)
        self.pontos = pontuacao_obtida
        self.tempo_total = tempo_gasto
        self.perfeito = not sofreu_dano

    def on_draw(self):
        self.clear()
        if self.perfeito:
            arcade.draw_text("DESEMPENHO PERFEITO!", DIMENSAO_X / 2, 450, arcade.color.GOLD, 32, anchor_x="center")
            arcade.draw_text("Parabéns! Você escapou de todos os inimigos impecavelmente!", DIMENSAO_X / 2, 380, arcade.color.LIGHT_GREEN, 16, anchor_x="center")
        else:
            arcade.draw_text("PARTIDA CONCLUÍDA!", DIMENSAO_X / 2, 450, arcade.color.WHITE, 32, anchor_x="center")
            arcade.draw_text("Parabéns por coletar todas as moedas do cenário!", DIMENSAO_X / 2, 380, arcade.color.LIGHT_BLUE, 16, anchor_x="center")

        arcade.draw_text(f"Pontuação Final: {self.pontos} pontos", DIMENSAO_X / 2, 300, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text(f"Tempo Transcorrido: {int(self.tempo_total)} segundos", DIMENSAO_X / 2, 250, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("Pressione [M] para Voltar ao Menu | [ESC] para Sair", DIMENSAO_X / 2, 140, arcade.color.LIGHT_GRAY, 16, anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.M:
            self.window.show_view(TelaMenuPrincipal())
        elif tecla == arcade.key.ESCAPE:
            arcade.close_window()


class TelaPartidaAtiva(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)
        self.fundo_mapa = arcade.load_texture("cenario.png")

        self.ritmo_movimento = 3.5
        self.placar = 0
        self.momento_inicio = time.time()
        self.temporizador_alerta = 0
        self.teve_dano = False

        self.grupo_heroi = arcade.SpriteList()
        self.grupo_tesouros = arcade.SpriteList()
        self.grupo_inimigos_comuns = arcade.SpriteList()
        self.grupo_inimigo_especial = arcade.SpriteList()
        # NOVO: lista de blocos (chão + plataformas)
        self.grupo_blocos = arcade.SpriteList()

        self.jogador = PersonagemHeroi()
        self.jogador.left = 10
        self.jogador.bottom = 100
        self.grupo_heroi.append(self.jogador)
        moedas_pos = [(200, 280), (450, 360), (650, 280)]
        for x, y in moedas_pos:
            self.grupo_tesouros.append(ItemMoedaPadrao(x, y))

        moeda_especial = ItemMoedaEspecial(100, 100, 2)
        self.grupo_tesouros.append(moeda_especial)

        inimigo_comum = ObstaculoRegular(400, 300, 3)
        self.grupo_inimigos_comuns.append(inimigo_comum)

        self.perseguidor = ObstaculoPerseguidor(700, 500)
        self.grupo_inimigo_especial.append(self.perseguidor)

        # ---------------------------------------------------------
        # NOVO: monta o chão (fileira de blocos na base da tela)
        # ---------------------------------------------------------
        for x in range(32, DIMENSAO_X + 32, 64):
            chao = Bloco(x, 20)
            self.grupo_blocos.append(chao)

        # NOVO: algumas plataformas flutuantes (opcional)
        posicoes_plataforma = [(200, 180), (450, 260), (650, 180)]
        for x, y in posicoes_plataforma:
            self.grupo_blocos.append(Bloco(x, y))

        # ---------------------------------------------------------
        # NOVO: motor de física de plataforma (aplica a GRAVIDADE
        # e resolve colisões do jogador com os blocos do chão)
        # ---------------------------------------------------------
        self.engine_fisica = arcade.PhysicsEnginePlatformer(
            player_sprite=self.jogador,
            walls=self.grupo_blocos,
            gravity_constant=GRAVIDADE
        )

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            texture=self.fundo_mapa,
            rect=arcade.XYWH(x=DIMENSAO_X / 2, y=DIMENSAO_Y / 2, width=DIMENSAO_X, height=DIMENSAO_Y)
        )

        self.grupo_blocos.draw()
        self.grupo_tesouros.draw()
        self.grupo_inimigos_comuns.draw()
        self.grupo_inimigo_especial.draw()
        self.grupo_heroi.draw()

        tempo_decorrido = int(time.time() - self.momento_inicio)
        arcade.draw_text(f"Pontos: {self.placar}", 15, 570, arcade.color.WHITE, 16)
        arcade.draw_text(f"Tempo: {tempo_decorrido}s", 15, 540, arcade.color.WHITE, 16)

        if self.temporizador_alerta > 0:
            arcade.draw_text("ALERTA: VOCÊ SOFREU DANO! (-1)", DIMENSAO_X / 2, 530, arcade.color.RED, 20, anchor_x="center")

    def on_update(self, delta_time):
        # ---------------------------------------------------------
        # NOVO: o motor de física é quem move o jogador no eixo Y
        # (aplica a gravidade e resolve colisão com os blocos).
        # ---------------------------------------------------------
        self.engine_fisica.update()

        # Chamamos o update() do jogador só para animação/textura e eixo X
        self.jogador.update(delta_time)

        self.grupo_tesouros.update(delta_time)
        self.grupo_inimigos_comuns.update(delta_time)
        self.perseguidor.perseguir_alvo(self.jogador.center_x, self.jogador.center_y)

        if self.temporizador_alerta > 0:
            self.temporizador_alerta -= delta_time

        moedas_atingidas = arcade.check_for_collision_with_list(self.jogador, self.grupo_tesouros)
        for moeda in moedas_atingidas:
            if isinstance(moeda, ItemMoedaEspecial):
                self.placar += 5
            else:
                self.placar += 1
            moeda.remove_from_sprite_lists()

        inimigos_comuns_colididos = arcade.check_for_collision_with_list(self.jogador, self.grupo_inimigos_comuns)
        if inimigos_comuns_colididos and not self.jogador.em_iframe:
            self.placar -= 1
            self.temporizador_alerta = 0.5
            self.teve_dano = True
            self.jogador.em_iframe = True
            self.jogador.tempo_iframe = 1.0

        if arcade.check_for_collision(self.jogador, self.perseguidor):
            if not self.jogador.em_iframe:
                self.placar -= 1
                self.temporizador_alerta = 0.5
                self.teve_dano = True
                self.jogador.em_iframe = True
                self.jogador.tempo_iframe = 1.0
            self.perseguidor.relocar_aleatoriamente()

        if self.placar < 0:
            self.window.show_view(TelaGameOver())
            return

        if len(self.grupo_tesouros) == 0:
            duracao = time.time() - self.momento_inicio
            self.window.show_view(TelaFinalizacao(self.placar, duracao, self.teve_dano))

    def on_key_press(self, tecla, modificadores):
        # Movimento lateral (eixo X) continua manual
        if tecla in (arcade.key.RIGHT, arcade.key.D):
            self.jogador.change_x = self.ritmo_movimento
        elif tecla in (arcade.key.LEFT, arcade.key.A):
            self.jogador.change_x = -self.ritmo_movimento

        # ---------------------------------------------------------
        # NOVO: pulo. Só pula se estiver encostado em um bloco
        # (evita "pulo infinito" no ar).
        # ---------------------------------------------------------
        if tecla in (arcade.key.UP, arcade.key.W, arcade.key.SPACE):
            if self.engine_fisica.can_jump():
                self.jogador.change_y = FORCA_PULO

        if tecla == arcade.key.ESCAPE:
            self.window.show_view(TelaMenuPrincipal())

    def on_key_release(self, tecla, modificadores):
        if tecla in (arcade.key.LEFT, arcade.key.A):
            if self.window.keyboard[arcade.key.RIGHT] or self.window.keyboard[arcade.key.D]:
                self.jogador.change_x = self.ritmo_movimento
            else:
                self.jogador.change_x = 0

        elif tecla in (arcade.key.RIGHT, arcade.key.D):
            if self.window.keyboard[arcade.key.LEFT] or self.window.keyboard[arcade.key.A]:
                self.jogador.change_x = -self.ritmo_movimento
            else:
                self.jogador.change_x = 0

        # Não precisamos mais zerar change_y no release: a gravidade
        # e o motor de física cuidam do eixo Y sozinhos.


def iniciar_sistema():
    janela_principal = arcade.Window(DIMENSAO_X, DIMENSAO_Y, TITULO_SISTEMA)
    janela_principal.show_view(TelaMenuPrincipal())
    arcade.run()


if __name__ == "__main__":
    iniciar_sistema()
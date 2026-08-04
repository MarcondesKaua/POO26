import arcade
import random
import time

ALTURA = 600
LARGURA = 800
TITULO = "Meu Jogo"
VELOCIDADE = 5
VELOCIDADE_PULO = 15
GRAVIDADE = 0.8


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("front.png", 5)
        self.center_x = 100
        self.center_y = 200
        self.i_frame = False
        self.i_frame_time = 0.0


class Inimigo(arcade.Sprite):
    def __init__(self, x, y, pequeno=False):
        escala = 0.5 if pequeno else 1
        super().__init__("fantasma_right.png", escala)
        self.center_x = x
        self.center_y = y
        self.change_x = 2 if not pequeno else 3
        self.change_y = 2 if not pequeno else 3
        
        self.pequeno = pequeno
        self.textura_direita = self.texture
        self.textura_esquerda = arcade.load_texture("fantasma_left.png")

    def teleportar(self):
        self.center_x = random.randint(50, LARGURA - 50)
        self.center_y = random.randint(100, ALTURA - 50)

    def on_update(self, player=None):
        if not self.pequeno and player is not None:
            velocidade_fantasma = 1.5
            if self.center_x < player.center_x:
                self.center_x += velocidade_fantasma
                self.texture = self.textura_direita
            elif self.center_x > player.center_x:
                self.center_x -= velocidade_fantasma
                self.texture = self.textura_esquerda

            if self.center_y < player.center_y:
                self.center_y += velocidade_fantasma
            elif self.center_y > player.center_y:
                self.center_y -= velocidade_fantasma
        else:
            self.center_x += self.change_x
            self.center_y += self.change_y

            if self.right >= LARGURA:
                self.right = LARGURA
                self.change_x *= -1
                self.texture = self.textura_esquerda

            if self.left <= 0:
                self.left = 0
                self.change_x *= -1
                self.texture = self.textura_direita

            if self.top > ALTURA:
                self.top = ALTURA
                self.change_y *= -1

            if self.bottom < 0:
                self.bottom = 0
                self.change_y *= -1


class Coin(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("coin.png", 1)
        self.center_x = x
        self.center_y = y


class TelaInicial(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.draw_text("COLETOR DE MOEDAS", LARGURA / 2, 420, arcade.color.WHITE, 32, anchor_x="center")
        arcade.draw_text("Pressione [J] para Jogar", LARGURA / 2, 330, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")
        arcade.draw_text("Pressione [T] para Tutorial", LARGURA / 2, 280, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")
        arcade.draw_text("Pressione [D] para Desenvolvedores", LARGURA / 2, 230, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para Sair", LARGURA / 2, 180, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.J:
            tela_jogo = JogoView() 
            tela_jogo.setup()
            self.window.show_view(tela_jogo) 
        elif key == arcade.key.T:
            tela_tutorial = TelaTutorial()
            self.window.show_view(tela_tutorial)
        elif key == arcade.key.D:
            tela_dev = TelaDesenvolvedores()
            self.window.show_view(tela_dev)
        elif key == arcade.key.ESCAPE:
            arcade.close_window()


class TelaTutorial(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)
        arcade.draw_text("TUTORIAL", LARGURA / 2, 450, arcade.color.WHITE, 28, anchor_x="center")
        arcade.draw_text("• Use SETAS para mover para os lados.", LARGURA / 2, 360, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("• Use ESPAÇO ou SETA PARA CIMA para pular.", LARGURA / 2, 310, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("• Colete 25 moedas o mais rápido possível para vencer!", LARGURA / 2, 260, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("• Cuidado com os fantasmas para não perder pontos.", LARGURA / 2, 210, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para voltar ao menu", LARGURA / 2, 100, arcade.color.GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)


class TelaDesenvolvedores(arcade.View):
    def __init__(self):
        super().__init__()

        self.lista_icones = arcade.SpriteList()

        self.fantasma_icon = arcade.Sprite("fantasma_right.png", scale=0.8)
        self.fantasma_icon.center_x = LARGURA / 2 - 130
        self.fantasma_icon.center_y = 338

        self.fantasma_icon2 = arcade.Sprite("fantasma_left.png", scale=0.8)
        self.fantasma_icon2.center_x = LARGURA / 2 - 150
        self.fantasma_icon2.center_y = 278

        self.lista_icones.append(self.fantasma_icon)
        self.lista_icones.append(self.fantasma_icon2)

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.CHARCOAL)
        arcade.draw_text("DESENVOLVEDORES", LARGURA / 2, 420, arcade.color.GOLD, 28, anchor_x="center")
        
        self.lista_icones.draw()
        arcade.draw_text("Kauã Marcondes", LARGURA / 2 + 20, 330, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Matheus Vinicius Geraldo", LARGURA / 2, 270, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para voltar ao menu", LARGURA / 2, 120, arcade.color.GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)


class TelaVitoria(arcade.View):
    def __init__(self, tempo_total=0, sem_dano=False):
        super().__init__()
        self.tempo_total = tempo_total
        self.sem_dano = sem_dano

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_text("Você venceu, parabens, coletou 25 moedas", LARGURA / 2, ALTURA / 2 + 50, arcade.color.WHITE, 20, anchor_x="center")
        
        if self.sem_dano:
            arcade.draw_text("Parabens você nao foi atingido nenhuma vez", LARGURA / 2, ALTURA / 2 + 10, arcade.color.SPRING_GREEN, 18, anchor_x="center", bold=True)

        arcade.draw_text(f"Tempo total: {int(self.tempo_total)}s", LARGURA / 2, ALTURA / 2 - 30, arcade.color.GOLD, 18, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para voltar ao menu", LARGURA / 2, ALTURA / 2 - 80, arcade.color.GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)


class TelaGameOver(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_text("Game over, você ficou devendo pros fantasmas", LARGURA / 2, ALTURA / 2, arcade.color.RED, 20, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para voltar ao menu", LARGURA / 2, ALTURA / 2 - 50, arcade.color.GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)


class JogoView(arcade.View):
    def __init__(self):
        super().__init__()
        self.fundo = arcade.load_texture("ceu.jpg")
        self.player = None
        self.lista_inimigos = None
        self.lista_player = None
        self.lista_plataformas = None
        self.lista_moedas = None
        self.fisica = None
        self.pontuacao = 0
        self.respawn_timer = 0.0
        self.aguardando_respawn = False
        self.tempo_inicio = 0.0
        self.timer_alerta = 0.0
        self.tomou_dano = False  # Controle de dano sofrido na partida

    def on_show_view(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        self.pontuacao = 0
        self.respawn_timer = 0.0
        self.aguardando_respawn = False
        self.tempo_inicio = time.time()
        self.timer_alerta = 0.0
        self.tomou_dano = False
        self.player = Player()

        self.lista_player = arcade.SpriteList()
        self.lista_player.append(self.player)

        self.lista_inimigos = arcade.SpriteList()
        inimigos = Inimigo(500, 100, False)
        inimigos_pequeno1 = Inimigo(400, 100, True)
        inimigos_pequeno2 = Inimigo(600, 100, True)
        self.lista_inimigos.append(inimigos)
        self.lista_inimigos.append(inimigos_pequeno1)
        self.lista_inimigos.append(inimigos_pequeno2)

        self.lista_plataformas = arcade.SpriteList(use_spatial_hash=True)

        for x in range(0, LARGURA + 64, 64):
            chao = arcade.SpriteSolidColor(64, 20, arcade.color.DARK_GREEN)
            chao.center_x = x
            chao.center_y = 20
            self.lista_plataformas.append(chao)

        plataformas = [
            (200, 150), (400, 250), (600, 200), (300, 400), (550, 400),
        ]
        for px, py in plataformas:
            plat = arcade.SpriteSolidColor(128, 20, arcade.color.BROWN)
            plat.center_x = px
            plat.center_y = py
            self.lista_plataformas.append(plat)

        self.lista_moedas = arcade.SpriteList(use_spatial_hash=True)
        moedas_pos = [(200, 200), (400, 310), (600, 260), (300, 460), (550, 460)]
        for mx, my in moedas_pos:
            self.lista_moedas.append(Coin(mx, my))

        self.fisica = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=GRAVIDADE,
            walls=self.lista_plataformas
        )

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(texture=self.fundo, rect=arcade.XYWH(x=LARGURA/2, y=ALTURA/2, width=LARGURA, height=ALTURA))
        self.lista_plataformas.draw()
        self.lista_moedas.draw()
        self.lista_player.draw()
        self.lista_inimigos.draw()

        arcade.Text(
            f"Moedas: {self.pontuacao}",
            10, ALTURA - 30,
            arcade.color.RED,
            font_size=20,
            bold=True
        ).draw()

        tempo_decorrido = int(time.time() - self.tempo_inicio) if self.tempo_inicio else 0
        arcade.Text(
            f"Tempo: {tempo_decorrido}s",
            10, ALTURA - 60,
            arcade.color.WHITE,
            font_size=18,
            bold=True
        ).draw()

        if self.timer_alerta > 0:
            arcade.Text(
                "Você perdeu uma moeda",
                LARGURA / 2, ALTURA - 40,
                arcade.color.RED,
                font_size=20,
                bold=True,
                anchor_x="center"
            ).draw()

    def resetar_moedas(self):
        self.lista_moedas.clear()
        moedas_pos = [(200, 200), (400, 310), (600, 260), (300, 460), (550, 460)]
        for mx, my in moedas_pos:
            self.lista_moedas.append(Coin(mx, my))

    def on_update(self, delta_time):
        self.fisica.update()

        self.player.left = max(self.player.left, 0)
        self.player.right = min(self.player.right, LARGURA)
        for inimigo in self.lista_inimigos:
            inimigo.on_update(self.player)
            
        if self.player.top >= ALTURA:
            self.player.top = ALTURA
            self.player.change_y = 0

        if self.timer_alerta > 0:
            self.timer_alerta -= delta_time

        if self.player.i_frame:
            self.player.i_frame_time -= delta_time
            if self.player.i_frame_time <= 0:
                self.player.i_frame = False 

        colisao_inimigo = arcade.check_for_collision_with_list(
            self.player, self.lista_inimigos
        )
        for inimigo in colisao_inimigo:
            if inimigo.pequeno and self.player.i_frame:
                self.pontuacao -= 1
                self.timer_alerta = 1.5
                self.tomou_dano = True
                inimigo.teleportar()
            else:
                if not self.player.i_frame:
                    self.pontuacao -= 1
                    self.timer_alerta = 1.5
                    self.tomou_dano = True
                    self.player.i_frame = True
                    self.player.i_frame_time = 1.0

        moedas_coletadas = arcade.check_for_collision_with_list(
            self.player, self.lista_moedas
        )
        for moeda in moedas_coletadas:
            moeda.remove_from_sprite_lists()
            self.pontuacao += 1

        if self.pontuacao >= 25:
            tempo_total = time.time() - self.tempo_inicio
            tela_vitoria = TelaVitoria(tempo_total, sem_dano=not self.tomou_dano)
            self.window.show_view(tela_vitoria)
            return

        if self.pontuacao <= -1:
            tela_game_over = TelaGameOver()
            self.window.show_view(tela_game_over)
            return

        if len(self.lista_moedas) == 0:
            if not self.aguardando_respawn:
                self.aguardando_respawn = True
                self.respawn_timer = 0.5
            else:
                self.respawn_timer -= delta_time
                if self.respawn_timer <= 0:
                    self.resetar_moedas()
                    self.aguardando_respawn = False

        if self.player.top < 0:
            self.setup()      
          
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)
        elif key == arcade.key.LEFT:
            self.player.texture = arcade.load_texture("Left.png")
            self.player.change_x = -VELOCIDADE
        elif key == arcade.key.RIGHT:
            self.player.texture = arcade.load_texture("Rigth.png")
            self.player.change_x = VELOCIDADE
        elif key in (arcade.key.SPACE, arcade.key.UP):
            if self.fisica.can_jump():
                self.player.change_y = VELOCIDADE_PULO + 4
        elif key == arcade.key.R:
            self.resetar_moedas()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            if self.window.keyboard[arcade.key.RIGHT]:
                self.player.change_x = VELOCIDADE
                self.player.texture = arcade.load_texture("Rigth.png")
            else:
                self.player.change_x = 0
                self.player.texture = arcade.load_texture("front.png")
        elif key == arcade.key.RIGHT:
            if self.window.keyboard[arcade.key.LEFT]:
                self.player.change_x = -VELOCIDADE
                self.player.texture = arcade.load_texture("Left.png")
            else:
                self.player.change_x = 0
                self.player.texture = arcade.load_texture("front.png")


def main():
    janela = arcade.Window(LARGURA, ALTURA, TITULO)
    menu = TelaInicial()
    janela.show_view(menu)
    arcade.run()


if __name__ == "__main__":
    main()
import arcade
import random

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


class Coin(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("coin.png", 0.05)
        self.center_x = x
        self.center_y = y


class JogoView(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.lista_player = None
        self.lista_plataformas = None
        self.lista_moedas = None
        self.fisica = None
        self.pontuacao = 0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        self.pontuacao = 0
        self.player = Player()

        self.lista_player = arcade.SpriteList()
        self.lista_player.append(self.player)

        # --- Plataformas ---
        self.lista_plataformas = arcade.SpriteList(use_spatial_hash=True)

        # Chão
        for x in range(0, LARGURA + 64, 64):
            chao = arcade.SpriteSolidColor(64, 20, arcade.color.DARK_GREEN)
            chao.center_x = x
            chao.center_y = 20
            self.lista_plataformas.append(chao)

        # Plataformas flutuantes
        plataformas = [
            (200, 150), (400, 250), (600, 200), (300, 350), (550, 400),
        ]
        for px, py in plataformas:
            plat = arcade.SpriteSolidColor(128, 20, arcade.color.BROWN)
            plat.center_x = px
            plat.center_y = py
            self.lista_plataformas.append(plat)

        # --- Moedas ---

        self.lista_moedas = arcade.SpriteList(use_spatial_hash=True)
        moedas_pos = [(200, 200), (400, 310), (600, 260), (300, 410), (550, 460)]
        for mx, my in moedas_pos:
            self.lista_moedas.append(Coin(mx, my))

        for _ in range(5):
            mx = random.randint(50, LARGURA-50)
            my = random.randint(50, ALTURA - 50)
            self.lista_moedas.append(Coin(mx,my))

        # --- Física com gravidade ---
        self.fisica = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=GRAVIDADE,
            walls=self.lista_plataformas
        )

    def on_draw(self):
        self.clear()
        self.lista_plataformas.draw()
        self.lista_moedas.draw()
        self.lista_player.draw()

        arcade.Text(
            f"Moedas: {self.pontuacao}",
            10, ALTURA - 30,
            arcade.color.RED,
            font_size=20,
            bold=True
        ).draw()

    def resetar_moedas(self):
        self.lista_moedas.clear()
        moedas_pos = [(200, 200), (400, 310), (600, 260), (300, 410), (550, 460)]
        for mx, my in moedas_pos:
            self.lista_moedas.append(Coin(mx, my))

        for _ in range(500):
            mx = random.randint(50, LARGURA-50)
            my = random.randint(50, ALTURA - 50)
            self.lista_moedas.append(Coin(mx,my))


    def on_update(self, delta_time):
        self.fisica.update()

        # Limita horizontalmente
        self.player.left = max(self.player.left, 0)
        self.player.right = min(self.player.right, LARGURA)
        if self.player.top >= ALTURA:
            self.player.top = ALTURA
            self.player.change_y=0

        # Coleta moedas
        moedas_coletadas = arcade.check_for_collision_with_list(
            self.player, self.lista_moedas
        )
        for moeda in moedas_coletadas:
            moeda.remove_from_sprite_lists()
            self.pontuacao += 1

        # Caiu do mapa — reinicia
        if self.player.top < 0:
            self.setup()

       

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()
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
            # Se direita ainda estiver pressionada, continua indo pra direita
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


class JanelaJogo(arcade.Window):
    def __init__(self):
        super().__init__(LARGURA, ALTURA, TITULO)

    def setup(self):
        view = JogoView()
        view.setup()
        self.show_view(view)


def main():
    jogo = JanelaJogo()
    jogo.setup()
    arcade.run()


if __name__ == "__main__":
    main()
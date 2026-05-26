import arcade

ALTURA = 600
LARGURA = 800
TITULO = "Meu Jogo"
VELOCIDADE = 5


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("front.png", 10)
        self.center_x = LARGURA // 2
        self.center_y = ALTURA // 2

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y


class JanelaJogo(arcade.Window):
    def __init__(self, largura, altura, titulo):
        super().__init__(largura, altura, titulo)
        self.jogo_rodando = False
        self.player = None
        self.lista_sprites = None

    def iniciar_jogo(self):
        arcade.set_background_color(arcade.color.AMAZON)
        self.jogo_rodando = True
        self.player = Player()
        self.lista_sprites = arcade.SpriteList()
        self.lista_sprites.append(self.player)

    def on_draw(self):
        self.clear()
        if self.jogo_rodando and self.lista_sprites is not None:
            self.lista_sprites.draw()
        arcade.Text("Nojo", self.width / 2, self.height / 2 + 100,
                    arcade.color.WHITE, font_size=50,
                    anchor_x="center", anchor_y="center", bold=True).draw()

    def on_update(self, delta_time):
        if self.jogo_rodando:
            self.lista_sprites.update(delta_time)

    def on_key_press(self, key, modifiers):
        # Troca o sprite E define a velocidade
        if key == arcade.key.LEFT:
            self.player.texture = arcade.load_texture("Left.png")
            self.player.change_x = -VELOCIDADE
        elif key == arcade.key.RIGHT:
            self.player.texture = arcade.load_texture("Rigth.png")
            self.player.change_x = VELOCIDADE
        elif key == arcade.key.UP:
            self.player.change_y = VELOCIDADE
        elif key == arcade.key.DOWN:
            self.player.texture = arcade.load_texture("Back.png")
            self.player.change_y = -VELOCIDADE

    def on_key_release(self, key, modifiers):
        # Para o movimento E volta para o sprite frontal
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.texture = arcade.load_texture("front.png")
            self.player.change_x = 0
        elif key in (arcade.key.UP, arcade.key.DOWN):
            self.player.texture = arcade.load_texture("front.png")
            self.player.change_y = 0


def main():
    jogo = JanelaJogo(LARGURA, ALTURA, TITULO)
    jogo.iniciar_jogo()
    arcade.run()


if __name__ == "__main__":
    main()
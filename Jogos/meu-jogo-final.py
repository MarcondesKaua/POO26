import arcade
import random
import time

from banco import db, Pontuacao, inicializar_banco, buscar_top10

DIMENSAO_X = 800
DIMENSAO_Y = 600
TITULO_SISTEMA = "Coletor do Tesouro - POO"
LIMITE_NOME = 12

DURACAO_INVENCIVEL = 1.5
DURACAO_FLASH = 0.3
DURACAO_TREMOR = 0.35
FORCA_TREMOR = 8

GRAVIDADE = 0.5
FORCA_PULO = 14


class BlocoPlataforma(arcade.Sprite):

    def __init__(self, pos_x, pos_y, imagem="bloco2.png"):
        super().__init__(imagem, scale=1)
        self.center_x = pos_x
        self.center_y = pos_y


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


class PersonagemHeroi(arcade.Sprite):
    def __init__(self):
        super().__init__("direita.png", scale=0.15)
        self.skin_direita = arcade.load_texture("direita.png")
        self.skin_esquerda = arcade.load_texture("esquerda.png")

    def atualizar_skin(self):
        if self.change_x > 0:
            self.texture = self.skin_direita
        elif self.change_x < 0:
            self.texture = self.skin_esquerda


class ObstaculoGravidade(arcade.Sprite):

    def __init__(self, pos_x, pos_y, plataformas):
        super().__init__("InimigoDireita.png", scale=0.9)
        self.center_x = pos_x
        self.center_y = pos_y
        self.velocidade = 2.2
        self.forca_pulo = 15

        self.texture_right = self.texture
        self.texture_left = arcade.load_texture("InimigoEsquerda.png")
        self.color = arcade.color.PURPLE

        self.fisica = arcade.PhysicsEnginePlatformer(
            self,
            gravity_constant=GRAVIDADE,
            walls=plataformas
        )

    def atualizar(self, alvo):
        x_antes = self.center_x
        no_chao = self.fisica.can_jump()

        if self.center_x < alvo.center_x - 2:
            self.change_x = self.velocidade
            self.texture = self.texture_right
        elif self.center_x > alvo.center_x + 2:
            self.change_x = -self.velocidade
            self.texture = self.texture_left
        else:
            self.change_x = 0

        if no_chao and alvo.center_y > self.center_y + 30:
            self.change_y = self.forca_pulo

        self.fisica.update()

        moveu_pouco = abs(self.center_x - x_antes) < 0.3
        if self.change_x != 0 and moveu_pouco and no_chao:
            self.change_y = self.forca_pulo

        self.center_x = max(0, min(DIMENSAO_X, self.center_x))


class EfeitoExplosao(arcade.Sprite):

    def __init__(self, pos_x, pos_y, quadros, escala=1.0):
        super().__init__(quadros[0], scale=escala)
        self.center_x = pos_x
        self.center_y = pos_y

        self.quadros = quadros
        self.quadro_atual = 0
        self.tempo_animacao = 0.0

    def update(self, delta_time: float = 1 / 60):
        self.tempo_animacao += delta_time

        if self.tempo_animacao >= 0.06:
            self.tempo_animacao = 0.0
            self.quadro_atual += 1

            if self.quadro_atual >= len(self.quadros):
                self.remove_from_sprite_lists()
                return

            self.texture = self.quadros[self.quadro_atual]


class TelaMenuPrincipal(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()
        arcade.draw_text("COLETOR DE TESOUROS", DIMENSAO_X / 2, 440, arcade.color.WHITE, 30, anchor_x="center")
        arcade.draw_text("[J] Jogar Partida", DIMENSAO_X / 2, 350, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("[R] Ver o Ranking", DIMENSAO_X / 2, 305, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("[I] Instruções de Jogo", DIMENSAO_X / 2, 260, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("[S] Sobre os Desenvolvedores", DIMENSAO_X / 2, 215, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text("[ESC] Sair do Jogo", DIMENSAO_X / 2, 170, arcade.color.WHITE, 18, anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.J:
            self.window.show_view(TelaPartidaAtiva())
        elif tecla == arcade.key.R:
            self.window.show_view(TelaRanking())
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
        arcade.draw_text("• Ande com SETAS ou A/D e pule com ESPAÇO, SETA PARA CIMA ou W.", DIMENSAO_X / 2, 380, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("• Colete todas as moedas simples (+1pt) e especiais (+5pts).", DIMENSAO_X / 2, 330, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("• EVITE OS FANTASMAS: se sua pontuação ficar menor que 0, é GAME OVER!", DIMENSAO_X / 2, 280, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("• Depois de levar um golpe você fica imune por um instante.", DIMENSAO_X / 2, 230, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("• Colete todas as moedas para vencer e entrar no ranking.", DIMENSAO_X / 2, 180, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_text("Pressione [M] ou [ESC] para retornar ao Menu", DIMENSAO_X / 2, 100, arcade.color.LIGHT_GRAY, 15, anchor_x="center")

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
        self.nome_digitado = ""

    def on_draw(self):
        self.clear()
        if self.perfeito:
            arcade.draw_text("DESEMPENHO PERFEITO!", DIMENSAO_X / 2, 520, arcade.color.GOLD, 32, anchor_x="center")
            arcade.draw_text("Parabéns! Você escapou de todos os inimigos impecavelmente!", DIMENSAO_X / 2, 480, arcade.color.LIGHT_GREEN, 16, anchor_x="center")
        else:
            arcade.draw_text("PARTIDA CONCLUÍDA!", DIMENSAO_X / 2, 520, arcade.color.WHITE, 32, anchor_x="center")
            arcade.draw_text("Parabéns por coletar todas as moedas do cenário!", DIMENSAO_X / 2, 480, arcade.color.LIGHT_BLUE, 16, anchor_x="center")

        arcade.draw_text(f"Pontuação Final: {self.pontos} pontos", DIMENSAO_X / 2, 410, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text(f"Tempo Transcorrido: {self.tempo_total:.1f}s", DIMENSAO_X / 2, 370, arcade.color.GOLD, 18, anchor_x="center")

        arcade.draw_text("Digite seu nome para o ranking:", DIMENSAO_X / 2, 310, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_rect_outline(
            arcade.XYWH(DIMENSAO_X / 2, 260, 360, 50), arcade.color.WHITE, border_width=2)
        arcade.draw_text(self.nome_digitado + "_", DIMENSAO_X / 2, 260, arcade.color.YELLOW, 22,
                         anchor_x="center", anchor_y="center")

        arcade.draw_text("[ENTER] Salvar e ver o ranking     [ESC] Menu sem salvar",
                         DIMENSAO_X / 2, 180, arcade.color.LIGHT_GRAY, 14, anchor_x="center")

    def on_text(self, text):
        if text.isprintable() and len(self.nome_digitado) < LIMITE_NOME:
            self.nome_digitado += text

    def on_key_press(self, tecla, modificadores):
        if tecla == arcade.key.BACKSPACE:
            self.nome_digitado = self.nome_digitado[:-1]

        elif tecla in (arcade.key.ENTER, arcade.key.NUM_ENTER):
            nome = self.nome_digitado.strip()
            if nome:
                nova = self.salvar_pontuacao(nome)
                self.window.show_view(TelaRanking(destaque_id=nova.id))

        elif tecla == arcade.key.ESCAPE:
            self.window.show_view(TelaMenuPrincipal())

    def salvar_pontuacao(self, nome):
        return Pontuacao.create(
            nome_jogador=nome,
            pontos=self.pontos,
            tempo_partida=self.tempo_total,
        )


class TelaRanking(arcade.View):

    def __init__(self, destaque_id=None):
        super().__init__()
        arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)
        self.melhores = buscar_top10()
        self.destaque_id = destaque_id

    def on_draw(self):
        self.clear()

        arcade.draw_text("RANKING - TOP 10", DIMENSAO_X / 2, 540,
                         arcade.color.GOLD, 32, anchor_x="center", bold=True)

        if len(self.melhores) == 0:
            arcade.draw_text("Nenhuma pontuação ainda! Seja o primeiro.", DIMENSAO_X / 2, DIMENSAO_Y / 2,
                             arcade.color.WHITE, 20, anchor_x="center")
        else:
            y_cabecalho = 480
            arcade.draw_text("POS", 100, y_cabecalho, arcade.color.LIGHT_GRAY, 14)
            arcade.draw_text("JOGADOR", 160, y_cabecalho, arcade.color.LIGHT_GRAY, 14)
            arcade.draw_text("PONTOS", 450, y_cabecalho, arcade.color.LIGHT_GRAY, 14, anchor_x="right")
            arcade.draw_text("TEMPO", 560, y_cabecalho, arcade.color.LIGHT_GRAY, 14, anchor_x="right")
            arcade.draw_text("DATA", 700, y_cabecalho, arcade.color.LIGHT_GRAY, 14, anchor_x="right")

            for indice, p in enumerate(self.melhores):
                y = 440 - indice * 34

                cor = arcade.color.YELLOW if p.id == self.destaque_id else arcade.color.WHITE

                arcade.draw_text(f"{indice + 1}º", 100, y, cor, 16)
                arcade.draw_text(p.nome_jogador, 160, y, cor, 16)
                arcade.draw_text(str(p.pontos), 450, y, cor, 16, anchor_x="right")
                arcade.draw_text(f"{p.tempo_partida:.1f}s", 560, y, cor, 16, anchor_x="right")
                arcade.draw_text(p.data_hora.strftime("%d/%m/%Y"), 700, y, cor, 16, anchor_x="right")

        arcade.draw_text("[J] Jogar     [M] ou [ESC] Voltar ao menu",
                         DIMENSAO_X / 2, 50, arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, tecla, modificadores):
        if tecla in (arcade.key.J, arcade.key.ENTER):
            self.window.show_view(TelaPartidaAtiva())
        elif tecla in (arcade.key.M, arcade.key.ESCAPE):
            self.window.show_view(TelaMenuPrincipal())


class TelaPartidaAtiva(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.AMAZON)
        self.fundo_mapa = arcade.load_texture("cenario.png")

        self.ritmo_movimento = 5
        self.placar = 0
        self.momento_inicio = time.time()
        self.temporizador_alerta = 0
        self.teve_dano = False

        folha_explosao = arcade.load_spritesheet("explosao.png")
        self.quadros_explosao = folha_explosao.get_texture_grid(
            size=(128, 128), columns=6, count=6
        )
        self.grupo_efeitos = arcade.SpriteList()

        self.invencivel_restante = 0.0
        self.flash_restante = 0.0
        self.tremor_restante = 0.0

        self.camera = arcade.Camera2D()
        self.camera.position = (DIMENSAO_X / 2, DIMENSAO_Y / 2)

        self.grupo_heroi = arcade.SpriteList()
        self.grupo_tesouros = arcade.SpriteList()
        self.grupo_inimigos_comuns = arcade.SpriteList()
        self.grupo_inimigo_especial = arcade.SpriteList()
        self.grupo_inimigo_gravidade = arcade.SpriteList()

        self.grupo_plataformas = arcade.SpriteList(use_spatial_hash=True)

        for x in range(32, DIMENSAO_X + 32, 64):
            self.grupo_plataformas.append(BlocoPlataforma(x, 30, "bloco2.png"))

        plataformas_flutuantes = [
            (150, 190), (650, 190),
            (270, 320), (530, 320),
            (400, 450),
        ]
        for px, py in plataformas_flutuantes:
            for deslocamento in (-32, 32):
                self.grupo_plataformas.append(BlocoPlataforma(px + deslocamento, py))

        for x in (40, 250, 310, 370, 430, 490, 550, 760):
            self.grupo_tesouros.append(ItemMoedaPadrao(x, 100))

        for px, py in plataformas_flutuantes:
            for deslocamento in (-48, 0, 48):
                self.grupo_tesouros.append(ItemMoedaPadrao(px + deslocamento, py + 55))

        moeda_especial = ItemMoedaEspecial(100, 100, 2)
        self.grupo_tesouros.append(moeda_especial)

        self.jogador = PersonagemHeroi()
        self.jogador.center_x = 400
        self.jogador.center_y = 150
        self.grupo_heroi.append(self.jogador)

        inimigo_comum = ObstaculoRegular(700, 450, 3)
        self.grupo_inimigos_comuns.append(inimigo_comum)

        self.perseguidor = ObstaculoPerseguidor(700, 500)
        self.grupo_inimigo_especial.append(self.perseguidor)

        self.inimigo_gravidade = ObstaculoGravidade(
            600, DIMENSAO_Y - 50, self.grupo_plataformas)
        self.grupo_inimigo_gravidade.append(self.inimigo_gravidade)

        self.fisica = arcade.PhysicsEnginePlatformer(
            self.jogador,
            gravity_constant=GRAVIDADE,
            walls=self.grupo_plataformas
        )

    def on_draw(self):
        self.clear()

        self.camera.use()

        arcade.draw_texture_rect(
            texture=self.fundo_mapa,
            rect=arcade.XYWH(
                x=DIMENSAO_X / 2,
                y=DIMENSAO_Y / 2,
                width=DIMENSAO_X + 2 * FORCA_TREMOR,
                height=DIMENSAO_Y + 2 * FORCA_TREMOR
            )
        )

        self.grupo_plataformas.draw()
        self.grupo_tesouros.draw()
        self.grupo_inimigos_comuns.draw()
        self.grupo_inimigo_especial.draw()
        self.grupo_inimigo_gravidade.draw()
        self.grupo_heroi.draw()
        self.grupo_efeitos.draw()

        self.window.default_camera.use()

        if self.flash_restante > 0:
            alpha = int(120 * self.flash_restante / DURACAO_FLASH)
            arcade.draw_rect_filled(
                arcade.XYWH(DIMENSAO_X / 2, DIMENSAO_Y / 2, DIMENSAO_X, DIMENSAO_Y),
                (255, 0, 0, alpha)
            )

        tempo_decorrido = int(time.time() - self.momento_inicio)
        arcade.draw_text(f"Pontos: {self.placar}", 15, 570, arcade.color.WHITE, 16)
        arcade.draw_text(f"Tempo: {tempo_decorrido}s", 15, 540, arcade.color.WHITE, 16)

        if self.temporizador_alerta > 0:
            arcade.draw_text("ALERTA: VOCÊ SOFREU DANO! (-1)", DIMENSAO_X / 2, 530, arcade.color.RED, 20, anchor_x="center")

    def on_update(self, delta_time):
        self.fisica.update()
        self.jogador.atualizar_skin()

        self.jogador.left = max(self.jogador.left, 0)
        self.jogador.right = min(self.jogador.right, DIMENSAO_X)
        if self.jogador.top >= DIMENSAO_Y:
            self.jogador.top = DIMENSAO_Y
            self.jogador.change_y = 0

        self.grupo_tesouros.update(delta_time)
        self.grupo_inimigos_comuns.update(delta_time)
        self.perseguidor.perseguir_alvo(self.jogador.center_x, self.jogador.center_y)
        self.inimigo_gravidade.atualizar(self.jogador)

        if self.temporizador_alerta > 0:
            self.temporizador_alerta -= delta_time

        self.invencivel_restante = max(0.0, self.invencivel_restante - delta_time)
        self.flash_restante = max(0.0, self.flash_restante - delta_time)
        self.tremor_restante = max(0.0, self.tremor_restante - delta_time)

        self.grupo_efeitos.update(delta_time)

        moedas_atingidas = arcade.check_for_collision_with_list(self.jogador, self.grupo_tesouros)
        for moeda in moedas_atingidas:
            if isinstance(moeda, ItemMoedaEspecial):
                self.placar += 5
            else:
                self.placar += 1
            moeda.remove_from_sprite_lists()

        if self.invencivel_restante == 0:
            colisoes = (
                arcade.check_for_collision_with_list(self.jogador, self.grupo_inimigos_comuns)
                + arcade.check_for_collision_with_list(self.jogador, self.grupo_inimigo_especial)
                + arcade.check_for_collision_with_list(self.jogador, self.grupo_inimigo_gravidade)
            )
            if colisoes:
                inimigo = colisoes[0]

                x = (self.jogador.center_x + inimigo.center_x) / 2
                y = (self.jogador.center_y + inimigo.center_y) / 2

                self.placar -= 1
                self.temporizador_alerta = 0.5
                self.teve_dano = True

                if inimigo is self.perseguidor:
                    self.perseguidor.relocar_aleatoriamente()

                self.grupo_efeitos.append(
                    EfeitoExplosao(x, y, self.quadros_explosao, escala=1.2))
                self.invencivel_restante = DURACAO_INVENCIVEL
                self.flash_restante = DURACAO_FLASH
                self.tremor_restante = DURACAO_TREMOR

        if self.invencivel_restante > 0:
            if int(self.invencivel_restante * 10) % 2 == 0:
                self.jogador.alpha = 80
            else:
                self.jogador.alpha = 255
        else:
            self.jogador.alpha = 255

        if self.tremor_restante > 0:
            forca = FORCA_TREMOR * self.tremor_restante / DURACAO_TREMOR
            self.camera.position = (
                DIMENSAO_X / 2 + random.uniform(-forca, forca),
                DIMENSAO_Y / 2 + random.uniform(-forca, forca),
            )
        else:
            self.camera.position = (DIMENSAO_X / 2, DIMENSAO_Y / 2)

        if self.placar < 0:
            self.window.show_view(TelaGameOver())
            return

        if len(self.grupo_tesouros) == 0:
            duracao = time.time() - self.momento_inicio
            self.window.show_view(TelaFinalizacao(self.placar, duracao, self.teve_dano))

    def on_key_press(self, tecla, modificadores):
        if tecla in (arcade.key.RIGHT, arcade.key.D):
            self.jogador.change_x = self.ritmo_movimento
        elif tecla in (arcade.key.LEFT, arcade.key.A):
            self.jogador.change_x = -self.ritmo_movimento
        elif tecla in (arcade.key.SPACE, arcade.key.UP, arcade.key.W):
            if self.fisica.can_jump():
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


def iniciar_sistema():
    inicializar_banco()

    janela_principal = arcade.Window(DIMENSAO_X, DIMENSAO_Y, TITULO_SISTEMA)
    janela_principal.show_view(TelaMenuPrincipal())
    arcade.run()

    db.close()


if __name__ == "__main__":
    iniciar_sistema()
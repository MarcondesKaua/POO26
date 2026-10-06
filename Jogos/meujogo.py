import arcade
import random
import time

# Tudo o que é banco de dados mora em banco.py; aqui só usamos o que precisamos
from banco import db, Pontuacao, inicializar_banco, buscar_top10

ALTURA = 600
LARGURA = 800
TITULO = "Meu Jogo"
VELOCIDADE = 5
VELOCIDADE_PULO = 10
GRAVIDADE = 0.5
LIMITE_NOME = 12   # Quantidade máxima de caracteres no nome do jogador

# Duração (em segundos) de cada efeito da colisão (Parte 4)
TEMPO_INVENCIVEL = 1.5     # Tempo em que o jogador fica imune depois de ser atingido
TEMPO_FLASH = 0.3          # Duração do clarão vermelho
TEMPO_TREMOR = 0.35        # Duração do tremor de tela
INTENSIDADE_TREMOR = 8     # Deslocamento máximo da câmera, em pixels


class Bloco(arcade.Sprite):
    """
    Mesmo Bloco do molde: um sprite de chão/plataforma feito a partir de
    uma imagem ("bloco.png"), em vez de um retângulo colorido gerado por
    código (arcade.SpriteSolidColor).
    """

    def __init__(self, x: float, y: float):
        super().__init__("bloco.png", scale=0.25)
        self.center_x = x
        self.center_y = y


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("front.png", 5)
        self.center_x = 100
        self.center_y = 200
        # A imunidade agora é controlada pelo temporizador tempo_invencivel
        # que fica no JogoView (Parte 4), então o i_frame antigo saiu daqui.


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


class InimigoGravidade(arcade.Sprite):
    """
    Fantasma que sofre efeito da gravidade (cai e fica em cima das
    plataformas, igual o player) e persegue o player horizontalmente,
    igual o fantasma grande. Pra diferenciar visualmente sem precisar
    de uma imagem nova, ele usa uma cor de "tint" por cima da textura.
    """

    def __init__(self, x, y):
        super().__init__("fantasma_right.png", 0.9)
        self.center_x = x
        self.center_y = y
        self.velocidade = 2.2
        self.forca_pulo = 15

        # Usado no on_update do JogoView e na checagem de dano, pra ele se
        # comportar igual o fantasma grande (não teleporta, tira i-frame).
        self.pequeno = False

        self.textura_direita = self.texture
        self.textura_esquerda = arcade.load_texture("fantasma_left.png")

        # Tinge o fantasma de outra cor (ele continua sendo o mesmo sprite,
        # só multiplica a textura por essa cor). Se quiser outra cor, é só
        # trocar esse valor.
        self.color = arcade.color.PURPLE

    def teleportar(self):
        # Mantido só por compatibilidade, caso algum outro trecho do código
        # chame teleportar() em qualquer inimigo. Esse fantasma não usa isso.
        self.center_x = random.randint(50, LARGURA - 50)
        self.center_y = ALTURA - 50

    def decidir_direcao(self, player):
        # A gravidade e a colisão com as plataformas quem cuida agora é o
        # PhysicsEnginePlatformer (criado no JogoView.setup()), igual já
        # acontecia com o player. Aqui só decidimos o change_x (pra que
        # lado andar) e trocamos a textura — o resto o engine resolve.
        if self.center_x < player.center_x - 2:
            self.change_x = self.velocidade
            self.texture = self.textura_direita
        elif self.center_x > player.center_x + 2:
            self.change_x = -self.velocidade
            self.texture = self.textura_esquerda
        else:
            self.change_x = 0


class Coin(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__("coin.png", 1)
        self.center_x = x
        self.center_y = y


# ==========================================
# CLASSE EXPLOSAO (EFEITO VISUAL DA COLISÃO)
# ==========================================
class Explosao(arcade.Sprite):
    """
    Efeito de explosão animado por spritesheet.
    Toca a animação uma única vez e se remove sozinho ao terminar.
    """

    def __init__(self, x: float, y: float, quadros: list, scale: float = 1.0):
        # Começa mostrando o primeiro quadro da animação
        super().__init__(quadros[0], scale=scale)

        # Posiciona o centro da explosão no ponto recebido
        self.center_x = x
        self.center_y = y

        # Guarda a lista de texturas (já fatiada) para trocar de quadro depois
        self.quadros = quadros
        self.quadro_atual = 0
        self.tempo_animacao = 0.0   # Acumula o tempo desde a última troca de quadro

    def update(self, delta_time: float = 1 / 60):
        # Soma o tempo que passou desde o quadro anterior
        self.tempo_animacao += delta_time

        # A cada 0,06 s (~16 quadros por segundo) avança um quadro da animação
        if self.tempo_animacao >= 0.06:
            self.tempo_animacao = 0.0
            self.quadro_atual += 1

            # Passou do último quadro? A explosão acabou: tira o sprite das listas
            if self.quadro_atual >= len(self.quadros):
                self.remove_from_sprite_lists()
                return

            # Ainda tem quadros: troca a textura mostrada
            self.texture = self.quadros[self.quadro_atual]


class TelaInicial(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        self.clear()
        arcade.draw_text("COLETOR DE MOEDAS", LARGURA / 2, 440,
                         arcade.color.WHITE, 32, anchor_x="center")
        arcade.draw_text("Pressione [J] para Jogar", LARGURA / 2,
                         360, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")
        arcade.draw_text("Pressione [R] para ver o Ranking", LARGURA / 2,
                         315, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")
        arcade.draw_text("Pressione [T] para Tutorial", LARGURA / 2,
                         270, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")
        arcade.draw_text("Pressione [D] para Desenvolvedores", LARGURA / 2,
                         225, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para Sair", LARGURA / 2,
                         180, arcade.color.LIGHT_SEA_GREEN, 18, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.J:
            tela_jogo = JogoView()
            tela_jogo.setup()
            self.window.show_view(tela_jogo)
        elif key == arcade.key.R:
            # Abre o ranking direto do menu (sem partida para destacar)
            self.window.show_view(TelaRanking())
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
        arcade.draw_text("TUTORIAL", LARGURA / 2, 450,
                         arcade.color.WHITE, 28, anchor_x="center")
        arcade.draw_text("• Use SETAS para mover para os lados.", LARGURA /
                         2, 360, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("• Use ESPAÇO ou SETA PARA CIMA para pular.",
                         LARGURA / 2, 310, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("• Colete 25 moedas o mais rápido possível para vencer!",
                         LARGURA / 2, 260, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("• Cuidado com os fantasmas para não perder pontos.",
                         LARGURA / 2, 210, arcade.color.LIGHT_GRAY, 16, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para voltar ao menu",
                         LARGURA / 2, 100, arcade.color.GRAY, 14, anchor_x="center")

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
        arcade.draw_text("DESENVOLVEDORES", LARGURA / 2, 420,
                         arcade.color.GOLD, 28, anchor_x="center")

        self.lista_icones.draw()
        arcade.draw_text("Kauã Marcondes", LARGURA / 2 + 20,
                         330, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Matheus Vinicius Geraldo", LARGURA / 2,
                         270, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para voltar ao menu",
                         LARGURA / 2, 120, arcade.color.GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)


class TelaVitoria(arcade.View):
    """
    Tela exibida ao vencer a partida.
    Mostra o resultado, pede o nome do jogador e salva a pontuação no banco (Parte 3).
    """

    def __init__(self, pontuacao=0, tempo_total=0, sem_dano=False):
        super().__init__()
        self.pontuacao = pontuacao
        self.tempo_total = tempo_total
        self.sem_dano = sem_dano
        # Texto que o jogador está digitando (começa vazio)
        self.nome_digitado = ""

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_text("Você venceu, parabens, coletou 25 moedas",
                         LARGURA / 2, 500, arcade.color.WHITE, 20, anchor_x="center")

        if self.sem_dano:
            arcade.draw_text("Parabens você nao foi atingido nenhuma vez", LARGURA / 2,
                             460, arcade.color.SPRING_GREEN, 18, anchor_x="center", bold=True)

        arcade.draw_text(f"Pontuação Final: {self.pontuacao} pontos",
                         LARGURA / 2, 415, arcade.color.WHITE, 18, anchor_x="center")
        arcade.draw_text(f"Tempo total: {self.tempo_total:.1f}s",
                         LARGURA / 2, 380, arcade.color.GOLD, 18, anchor_x="center")

        # Campo de nome: um retângulo com o texto digitado dentro
        arcade.draw_text("Digite seu nome para o ranking:", LARGURA / 2,
                         320, arcade.color.WHITE, 16, anchor_x="center")
        arcade.draw_rect_outline(arcade.XYWH(
            LARGURA / 2, 270, 360, 50), arcade.color.WHITE, border_width=2)
        # O "_" no final funciona como um cursor, mostrando onde a próxima letra entra
        arcade.draw_text(self.nome_digitado + "_", LARGURA / 2, 270, arcade.color.YELLOW, 22,
                         anchor_x="center", anchor_y="center")

        # Instruções
        arcade.draw_text("[ENTER] Salvar e ver o ranking     [ESC] Voltar ao menu sem salvar",
                         LARGURA / 2, 190, arcade.color.GRAY, 14, anchor_x="center")

    def on_text(self, text):
        # Chamado a cada caractere digitado (já com maiúsculas, acentos, espaço...)
        # isprintable() descarta caracteres de controle, como o "\r" do ENTER
        if text.isprintable() and len(self.nome_digitado) < LIMITE_NOME:
            self.nome_digitado += text

    def on_key_press(self, key, modifiers):
        # BACKSPACE: remove o último caractere
        if key == arcade.key.BACKSPACE:
            self.nome_digitado = self.nome_digitado[:-1]

        # ENTER (normal ou do teclado numérico): salva e abre o ranking
        elif key == arcade.key.ENTER or key == arcade.key.NUM_ENTER:
            nome = self.nome_digitado.strip()   # Remove espaços das pontas
            if nome:                            # Só salva se o nome não estiver vazio
                nova = self.salvar_pontuacao(nome)
                # Passa o id do registro novo para o ranking destacá-lo
                self.window.show_view(TelaRanking(destaque_id=nova.id))

        # ESC: desiste de salvar e volta ao menu
        elif key == arcade.key.ESCAPE:
            self.window.show_view(TelaInicial())

    def salvar_pontuacao(self, nome: str) -> Pontuacao:
        """Único ponto da tela que conversa com o banco: cria o registro."""
        return Pontuacao.create(
            nome_jogador=nome,
            pontos=self.pontuacao,
            tempo_partida=self.tempo_total,
        )


class TelaGameOver(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        self.clear()
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_text("Game over, você ficou devendo pros fantasmas",
                         LARGURA / 2, ALTURA / 2, arcade.color.RED, 20, anchor_x="center")
        arcade.draw_text("Pressione [ESC] para voltar ao menu", LARGURA / 2,
                         ALTURA / 2 - 50, arcade.color.GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            tela_inicial = TelaInicial()
            self.window.show_view(tela_inicial)


# ==========================================
# CLASSE TELA RANKING (TOP 10)
# ==========================================
class TelaRanking(arcade.View):
    """Exibe as 10 melhores pontuações salvas no banco de dados."""

    def __init__(self, destaque_id: int = None):
        super().__init__()
        # A consulta roda UMA vez, aqui no construtor — nunca no on_draw
        self.melhores = buscar_top10()
        # id da partida que acabou de ser salva (None quando viemos do menu)
        self.destaque_id = destaque_id

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_MIDNIGHT_BLUE)

    def on_draw(self):
        self.clear()

        arcade.draw_text("RANKING - TOP 10", LARGURA / 2, 540,
                         arcade.color.GOLD, 32, anchor_x="center", bold=True)

        # Caso especial: banco ainda vazio (o for abaixo não executaria nenhuma vez)
        if len(self.melhores) == 0:
            arcade.draw_text("Nenhuma pontuação ainda! Seja o primeiro.", LARGURA / 2, ALTURA / 2,
                             arcade.color.WHITE, 20, anchor_x="center")
        else:
            # Cabeçalho das colunas
            y_cabecalho = 480
            arcade.draw_text("POS", 100, y_cabecalho,
                             arcade.color.LIGHT_GRAY, 14)
            arcade.draw_text("JOGADOR", 160, y_cabecalho,
                             arcade.color.LIGHT_GRAY, 14)
            arcade.draw_text("PONTOS", 450, y_cabecalho,
                             arcade.color.LIGHT_GRAY, 14, anchor_x="right")
            arcade.draw_text("TEMPO", 560, y_cabecalho,
                             arcade.color.LIGHT_GRAY, 14, anchor_x="right")
            arcade.draw_text("DATA", 700, y_cabecalho,
                             arcade.color.LIGHT_GRAY, 14, anchor_x="right")

            # enumerate devolve o índice (0, 1, 2...) junto de cada objeto
            for indice, p in enumerate(self.melhores):
                # Cada linha fica 34 pixels abaixo da anterior
                y = 440 - indice * 34

                # A partida recém-salva aparece em amarelo
                if p.id == self.destaque_id:
                    cor = arcade.color.YELLOW
                else:
                    cor = arcade.color.WHITE

                arcade.draw_text(f"{indice + 1}º", 100, y, cor, 16)
                arcade.draw_text(p.nome_jogador, 160, y, cor, 16)
                arcade.draw_text(str(p.pontos), 450, y,
                                 cor, 16, anchor_x="right")
                arcade.draw_text(f"{p.tempo_partida:.1f}s",
                                 560, y, cor, 16, anchor_x="right")
                # data_hora volta do banco como datetime: strftime formata como dd/mm/aaaa
                arcade.draw_text(p.data_hora.strftime(
                    "%d/%m/%Y"), 700, y, cor, 16, anchor_x="right")

        arcade.draw_text("[J] Jogar     [ESC] Voltar ao menu",
                         LARGURA / 2, 50, arcade.color.WHITE, 16, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.J or key == arcade.key.ENTER:
            tela_jogo = JogoView()
            tela_jogo.setup()
            self.window.show_view(tela_jogo)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(TelaInicial())


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

        # ---- EFEITOS DE COLISÃO (Parte 4) ----
        # Quadros da explosão: carregados UMA vez, reaproveitados em cada explosão
        sheet_explosao = arcade.load_spritesheet("explosao.png")
        self.quadros_explosao = sheet_explosao.get_texture_grid(
            size=(128, 128), columns=6, count=6
        )
        # Lista de sprites só para os efeitos (as explosões)
        self.lista_efeitos = arcade.SpriteList()

        # Temporizadores dos efeitos: zero significa "desligado"
        self.tempo_invencivel = 0.0
        self.tempo_flash = 0.0
        self.tempo_tremor = 0.0

        # Câmera do mundo do jogo (usada para o tremor)
        self.camera = arcade.Camera2D()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def setup(self):
        self.pontuacao = 0
        self.respawn_timer = 0.0
        self.aguardando_respawn = False
        self.tempo_inicio = time.time()
        self.timer_alerta = 0.0
        self.tomou_dano = False

        # Zera os efeitos para a partida (re)começar limpa
        self.tempo_invencivel = 0.0
        self.tempo_flash = 0.0
        self.tempo_tremor = 0.0
        self.lista_efeitos = arcade.SpriteList()
        self.camera.position = (LARGURA / 2, ALTURA / 2)

        self.player = Player()

        self.lista_player = arcade.SpriteList()
        self.lista_player.append(self.player)

        self.lista_inimigos = arcade.SpriteList()
        inimigos = Inimigo(500, 100, False)
        inimigos_pequeno1 = Inimigo(400, 100, True)
        self.inimigo_gravidade = InimigoGravidade(600, ALTURA - 50)
        self.lista_inimigos.append(inimigos)
        self.lista_inimigos.append(inimigos_pequeno1)
        self.lista_inimigos.append(self.inimigo_gravidade)

        # SpriteList que vai guardar todas as plataformas (chão + blocos flutuantes).
        # use_spatial_hash=True: otimização de colisão. Divide o espaço da tela em
        # "células" (grid) e o Arcade só checa colisão contra sprites que estão na
        # mesma célula do player, em vez de checar contra TODOS os sprites da lista.
        # Só compensa pra objetos que não se movem (ou se movem raramente) — se
        # ativasse isso numa lista de sprites que mudam de posição todo frame
        # (tipo os inimigos), o custo de recalcular o hash a cada frame anularia
        # o ganho de performance.
        self.lista_plataformas = arcade.SpriteList(use_spatial_hash=True)

        # Cria o "chão" da fase, lado a lado, cobrindo toda a largura da tela.
        # Igual o molde: range(32, LARGURA + 32, 64) começa meio bloco pra
        # dentro (32 = metade de 64) e cada Bloco já nasce centralizado no x,
        # então os blocos ficam grudados um do lado do outro sem buraco.
        for x in range(32, LARGURA + 32, 64):
            chao = Bloco(x=x, y=30)
            self.lista_plataformas.append(chao)

        # Coordenadas (x, y) das plataformas flutuantes que o player pode pular
        # em cima. São fixas, escolhidas manualmente pra desenhar o layout da fase.
        plataformas = [
            (200, 150), (400, 250), (600, 200), (300, 400), (550, 400),
        ]
        for px, py in plataformas:
            plat = Bloco(px, py)
            self.lista_plataformas.append(plat)

        # Lista separada pras moedas — também usa spatial hash pelo mesmo motivo
        # das plataformas: moedas ficam paradas até serem coletadas, então vale
        # a pena otimizar a checagem de colisão contra elas.
        self.lista_moedas = arcade.SpriteList(use_spatial_hash=True)
        moedas_pos = [(200, 200), (400, 310), (600, 260),
                      (300, 460), (550, 460)]
        for mx, my in moedas_pos:
            self.lista_moedas.append(Coin(mx, my))

        # Motor de física pronto do Arcade, feito especificamente pra jogos de
        # plataforma (plataformer = jogo tipo Mario, com pulo e gravidade).
        # Ele cuida automaticamente de:
        #   - aplicar gravidade no player a cada frame (puxando ele pra baixo)
        #   - detectar quando o player está em cima de uma plataforma (pra permitir
        #     pular de novo, via fisica.can_jump())
        #   - impedir o player de atravessar as plataformas (colisão sólida)
        self.fisica = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=GRAVIDADE,
            walls=self.lista_plataformas
        )

        # Mesma ideia do engine acima, mas pro fantasma de gravidade. Cada
        # instância do PhysicsEnginePlatformer cuida de UM sprite só, então
        # precisa de uma segunda instância — mas nada impede de reusar a
        # mesma lista de plataformas como "walls" pras duas.
        self.fisica_inimigo_gravidade = arcade.PhysicsEnginePlatformer(
            self.inimigo_gravidade,
            gravity_constant=GRAVIDADE,
            walls=self.lista_plataformas
        )

    def on_draw(self):
        self.clear()

        # A partir daqui tudo é desenhado "através" da câmera que treme
        self.camera.use()

        # Cenário um pouco MAIOR que a tela, para não aparecer borda vazia
        # quando a câmera se desloca para os lados
        arcade.draw_texture_rect(
            texture=self.fundo,
            rect=arcade.XYWH(
                x=LARGURA / 2,
                y=ALTURA / 2,
                width=LARGURA + 2 * INTENSIDADE_TREMOR,
                height=ALTURA + 2 * INTENSIDADE_TREMOR
            )
        )
        self.lista_plataformas.draw()
        self.lista_moedas.draw()
        self.lista_player.draw()
        self.lista_inimigos.draw()
        self.lista_efeitos.draw()   # Explosões por cima de tudo

        # Volta para a câmera fixa da janela: flash e HUD não tremem
        self.window.default_camera.use()

        # Flash vermelho: alpha proporcional ao tempo restante
        if self.tempo_flash > 0:
            alpha = int(120 * self.tempo_flash / TEMPO_FLASH)
            arcade.draw_rect_filled(
                arcade.XYWH(LARGURA / 2, ALTURA / 2, LARGURA, ALTURA),
                (255, 0, 0, alpha)
            )

        # HUD
        arcade.Text(
            f"Moedas: {self.pontuacao}",
            10, ALTURA - 30,
            arcade.color.RED,
            font_size=20,
            bold=True
        ).draw()

        tempo_decorrido = int(
            time.time() - self.tempo_inicio) if self.tempo_inicio else 0
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
        moedas_pos = [(200, 200), (400, 310), (600, 260),
                      (300, 460), (550, 460)]
        for mx, my in moedas_pos:
            self.lista_moedas.append(Coin(mx, my))

    def on_update(self, delta_time):
        self.fisica.update()

        self.player.left = max(self.player.left, 0)
        self.player.right = min(self.player.right, LARGURA)
        for inimigo in self.lista_inimigos:
            # O InimigoGravidade não usa esse on_update: ele é movido pelo
            # self.fisica_inimigo_gravidade logo abaixo, igual o player.
            if inimigo is self.inimigo_gravidade:
                continue
            inimigo.on_update(self.player)

        # Fantasma de gravidade: decide pra que lado andar e se deve pular,
        # depois deixa o PhysicsEnginePlatformer aplicar gravidade/colisão.
        x_antes = self.inimigo_gravidade.center_x
        no_chao = self.fisica_inimigo_gravidade.can_jump()
        self.inimigo_gravidade.decidir_direcao(self.player)

        if no_chao and self.player.center_y > self.inimigo_gravidade.center_y + 30:
            # Player numa plataforma bem mais alta: tenta pular na direção dele.
            self.inimigo_gravidade.change_y = self.inimigo_gravidade.forca_pulo

        self.fisica_inimigo_gravidade.update()

        # Se ele tentou andar mas mal se moveu, é porque bateu numa parede
        # (o engine não deixa atravessar). Nesse caso ele pula no próximo
        # frame, em vez de ficar preso empurrando a parede pra sempre.
        moveu_pouco = abs(self.inimigo_gravidade.center_x - x_antes) < 0.3
        if self.inimigo_gravidade.change_x != 0 and moveu_pouco and no_chao:
            self.inimigo_gravidade.change_y = self.inimigo_gravidade.forca_pulo

        self.inimigo_gravidade.center_x = max(
            0, min(LARGURA, self.inimigo_gravidade.center_x))

        if self.player.top >= ALTURA:
            self.player.top = ALTURA
            self.player.change_y = 0

        if self.timer_alerta > 0:
            self.timer_alerta -= delta_time

        # Desconta o tempo dos efeitos (nunca abaixo de zero)
        self.tempo_invencivel = max(0.0, self.tempo_invencivel - delta_time)
        self.tempo_flash = max(0.0, self.tempo_flash - delta_time)
        self.tempo_tremor = max(0.0, self.tempo_tremor - delta_time)

        # Chama o update() de cada explosão viva
        self.lista_efeitos.update(delta_time)

        # Colisão com inimigos: só vale se o jogador NÃO estiver imune.
        # Tudo o que deve acontecer "uma vez por golpe" fica DENTRO deste if.
        if self.tempo_invencivel == 0:
            colisao_inimigo = arcade.check_for_collision_with_list(
                self.player, self.lista_inimigos
            )
            if colisao_inimigo:
                inimigo = colisao_inimigo[0]

                # Ponto de impacto: média entre os centros dos dois sprites
                x = (self.player.center_x + inimigo.center_x) / 2
                y = (self.player.center_y + inimigo.center_y) / 2

                # Consequências do golpe
                self.pontuacao -= 1
                self.timer_alerta = 1.5
                self.tomou_dano = True

                # Fantasma pequeno some do lugar do choque (teleporta)
                if inimigo.pequeno:
                    inimigo.teleportar()

                # Liga os quatro efeitos de uma vez
                self.lista_efeitos.append(
                    Explosao(x, y, self.quadros_explosao, scale=1.2))
                self.tempo_invencivel = TEMPO_INVENCIVEL
                self.tempo_flash = TEMPO_FLASH
                self.tempo_tremor = TEMPO_TREMOR

        moedas_coletadas = arcade.check_for_collision_with_list(
            self.player, self.lista_moedas
        )
        for moeda in moedas_coletadas:
            moeda.remove_from_sprite_lists()
            self.pontuacao += 1

        # Piscar: alterna a transparência a cada décimo de segundo
        if self.tempo_invencivel > 0:
            if int(self.tempo_invencivel * 10) % 2 == 0:
                self.player.alpha = 80     # Quase transparente
            else:
                self.player.alpha = 255    # Opaco
        else:
            # Acabou a imunidade: garante que o personagem volte a ficar 100% visível
            self.player.alpha = 255

        # Tremor: câmera sacode com força decrescente e volta ao centro no fim
        if self.tempo_tremor > 0:
            forca = INTENSIDADE_TREMOR * self.tempo_tremor / TEMPO_TREMOR
            self.camera.position = (
                LARGURA / 2 + random.uniform(-forca, forca),
                ALTURA / 2 + random.uniform(-forca, forca),
            )
        else:
            self.camera.position = (LARGURA / 2, ALTURA / 2)

        if self.pontuacao >= 25:
            tempo_total = time.time() - self.tempo_inicio
            tela_vitoria = TelaVitoria(
                pontuacao=self.pontuacao,
                tempo_total=tempo_total,
                sem_dano=not self.tomou_dano
            )
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
    # Prepara o banco ANTES de abrir a janela: arquivo e tabela garantidos
    inicializar_banco()

    janela = arcade.Window(LARGURA, ALTURA, TITULO)
    menu = TelaInicial()
    janela.show_view(menu)
    arcade.run()

    # Só chega aqui depois que a janela foi fechada: encerra a conexão
    db.close()


if __name__ == "__main__":
    main()

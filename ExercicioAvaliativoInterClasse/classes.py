class Equipes: 
    LIMITE_JOGADORES = 5
    def __init__(self):
        self.nome = ""
        self.modalidade = ""
        self.jogadores = []

        
    def cadastrar_jogador(self, jogador, todas_equipes):
        for equipe in todas_equipes:
            if jogador in equipe.jogadores:
                print(f"'{jogador.nome}' já está na equipe '{equipe.nome}'!")
                return

        
        if len(self.jogadores) >= self.LIMITE_JOGADORES:
            print(f"Equipe '{self.nome}' já tem {self.LIMITE_JOGADORES} jogadores (limite máximo)!")
            return

        self.jogadores.append(jogador)
        print(f"Jogador '{jogador.nome}' adicionado à equipe '{self.nome}' com sucesso!")

    def apresentar_equipe(self):
        return f"{self.nome} | Jogo: {self.modalidade} | Jogadores: {len(self.jogadores)}"

    def apresentar_jogadores_equipe(self):
        if not self.jogadores:
            print("  Nenhum jogador nessa equipe ainda.")
        else:
            for jogador in self.jogadores:
                print(f"  - {jogador.apresentar()}")
            
    def preencher_info(self):
        self.nome = input("Digite o nome da equipe: ")
        self.modalidade = input("Digite a modalidade: ")



class Jogadores:
    def __init__(self):
        self.nome = ""
        self.nickname = ""
        self.turma = ""

    def apresentar(self):
        return f"{self.nome} - {self.nickname} - {self.turma}"
    
    def preencher_info(self, list_jogadores):
        self.nome = input("Digite o nome do jogador: ")

        while(True):
            self.nickname = input("Digite o nickname: ")
            duplicado = any(j.nickname.lower() == self.nickname.lower() for j in list_jogadores)
            if duplicado:
                print("Esse nickname já existe! Tente outro.")
            else:
                break
        self.turma = input("Digite a turma: ")

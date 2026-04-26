class Equipes: 
    def __init__(self):
        self.nome = ""
        self.modalidade = ""
        self.jogadores = []

        
    def cadastrar_jogador(self, jogador):
        if jogador not in self.jogadores:
            self.jogadores.append(jogador)
        else:
            print(f"Jogar {jogador.nome} já está cadastrado nessa equipe")

    def apresentar_equipe(self):
        return self.nome
         

    def apresentar_jogadores_equipe(self):
        for i in self.jogadores: 
            print(i.apresentar())
            
    def preencher_info(self):
        self.nome = input("Digite o nome da equipe: ")
        self.modalidade = input("Digite a modalidade: ")



class Jogadores:
    def __init__(self):
        self.nome = ""
        self.nickname = ""
        self.turma = ""

    def apresentar(self):
        return f"{self.nome} - {self.nickname}"
    
    def preencher_info(self):
        self.nome = input("Digite o nome do jogador: ")
        self.nickname = input("Digite o nickname: ")
        self.turma = input("Digite a turma: ")

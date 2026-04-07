class Aluno:
    def __init__(self, nome, idade, curso):
        self.nome = nome
        self.idade = idade
        self.curso = curso

    def apresentar(self):
        print(f"Olá, meu nome é {self.nome}, tenho {self.idade} anos e estou cursando {self.curso}")


aluno1 = Aluno("Zotesso", 19, "Todos")
aluno1.apresentar()
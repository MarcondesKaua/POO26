class Aluno:
    def __init__(self, nome, idade, curso, notas = None):
        self.nome = nome
        self.idade = idade
        self.curso = curso

        if notas is None:
            self.notas= []
        else:
            self.notas = notas

    def apresentar(self):
        print(f"Olá, meu nome é {self.nome}, tenho {self.idade} anos e estou cursando {self.curso}")

    def calcular_media(self):
        media = sum(self.notas) / len(self.notas)
        return round(media, 2)
    

aluno1 = Aluno("Zotesso", 19, "Todos", [10,9,10])
aluno1.apresentar()
print(aluno1.calcular_media())


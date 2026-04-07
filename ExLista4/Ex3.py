class Livro:
    def __init__(self, nome):
        self.nome = nome 
        self.disp = True

    def emprestar(self):
        if self.disp:
            print(f"Livro {self.nome} está disponivel")

            self.disp = False
        else:
            print(f"O livro {self.nome} não está disponivel")

    def devolver(self):
        self.disp = True
        print(f"Livro {self.nome} devolvido com sucesso")


liv = Livro("Don Casmurro")
liv.emprestar()
liv.devolver()
liv.emprestar()
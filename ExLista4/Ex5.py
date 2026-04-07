class Contato:
    agenda = []
    def __init__(self, nome, telefone):
        self.nome = nome
        self.telefone = telefone
        Contato.agenda.append(self)
    def mostrar(self):
        print(f"{self.nome} - {self.telefone}")

cont1 = Contato("Zotesso", "9999-9999")
cont2 = Contato("Kauã", "998757190")

for pessoa in Contato.agenda:
    pessoa.mostrar()
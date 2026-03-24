class Campus: 
    def __init__(self):
        self.nome = ""
        self.endereco = ""

    def __str__(self):
        return f"Campus: {self.nome}"
    
class Estudante:
    def __init__(self):
        self.nome =""
        self.date_nasc = ""
        self.cpf = ""
    def __str__(self):
        return f"Estudante: {self.nome, self.cpf, self.date_nasc}"
    def print(self):
        print(self.nome, self.cpf, self.date_nasc)
    

estudante = Estudante()
estudante.nome = "Ryan"
estudante.cpf = "111-111-111.11"
estudante.date_nasc = "10/10/1000"

estudante.print()
print(estudante)

estudante2 = Estudante()
estudante2.nome = "Nayr"
estudante2.cpf = "000-000-00.00"
estudante2.date_nasc = "10/10/1000"

estudante2.print()

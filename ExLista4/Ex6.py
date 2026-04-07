class Estudante:
    def __init__(self, nome, idade, cpf):
        self.nome = nome
        if(type(idade)== int):
            self.idade = idade
        else:
            print("Erro")
        self.cpf = cpf

aln1 = Estudante("Kauã", 17, "1000")
aln2 = Estudante("Zotesso", 37, "000")
aln3 = Estudante("Joao Manoel", 67, "0202")

print(aln1.nome, aln1.idade, aln1.cpf)
print(aln2.nome, aln2.idade, aln2.cpf)
print(aln3.nome, aln3.idade, aln3.cpf)
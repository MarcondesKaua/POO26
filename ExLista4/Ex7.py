class Turma:
    def __init__(self, nome, ano, estudantes = None):
        self.nome = nome
        self.ano = ano

        if estudantes is None:
            self.estudantes = []
        else:
            self.estudantes = estudantes

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

tm1 = Turma("POO", 2025, [aln1, aln2])
tm2 = Turma("POO", 2026, [aln3])

print(tm1.nome, tm1.ano)
for aluno in tm1.estudantes:
    print(aluno.nome)

print(tm2.nome, tm2.ano)
for aluno in tm2.estudantes:
  print(aluno.nome)      

print("ALUNOS:  \n")
print(aln1.nome, aln1.idade, aln1.cpf)
print(aln2.nome, aln2.idade, aln2.cpf)
print(aln3.nome, aln3.idade, aln3.cpf)
#from seu_arquivo import SuaClasse
class Turma:
    def __init__(self, nome, ano, estudantes = None):
        self.nome = nome
        self.ano = ano

        if estudantes is None:
            self.estudantes = []
        else:
            self.estudantes = estudantes

    def exibir_estudantes(self):
        print(f"\nListando estudantes da turma {self.nome, self.ano} : \n")
        for aluno in self.estudantes:
            print(f"Alunos- Nome: {aluno.nome} Idade: {aluno.idade} CPF: {aluno.cpf}")
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


tm1.exibir_estudantes()
tm2.exibir_estudantes()

print("\nALUNOS: \n ")
print(aln1.nome, aln1.idade, aln1.cpf)
print(aln2.nome, aln2.idade, aln2.cpf)
print(aln3.nome, aln3.idade, aln3.cpf)
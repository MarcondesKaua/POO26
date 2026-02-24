name = input("Qual seu nome: ")
age = int(input("Idade: "))
payment = float(input("Qual seu salario: "))

if (payment <= 3000):
    print("Olá", name, "Você tem", age, "Seu salario de R$: ", payment, " é muito ruim")

elif (payment <= 10000): 
    print("Olá", name, "Você tem", age, "Seu salario de R$: ", payment, " é decente")

elif (payment< 20000) :
    print("Olá", name, "Você tem", age, "Seu salario de R$: ", payment, " é normal, da para pagar unimed")

else:
    print("Olá", name, "Você tem", age, "Seu salario de R$: ", payment, " é normal, bem vindo Jeff Bezos")
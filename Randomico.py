import random

# uservalid = True

# while (uservalid):

#     valor_user = int(input("Eu sorteei um valor, tente acertar, o numero vai de 1 a 15: "))


#     if valor_user < 1 or valor_user >15:
#         print("erro")
#     else:
#         uservalid = False


valor_user = -1
valor = random.randint(1, 15)


while not(valor_user == valor):
    try:
        valor_user = int(input("Eu sorteei um valor, tente acertar, o numero vai de 1 a 15: "))
        if not(1<= valor_user <=15):    
         print("O valor é ENTRE 1 e 15")
    except:
        print("Algum erro grande")
        continue
    


print("Você acertou")
print("O valor era: ", valor)    
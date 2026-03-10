import os

comandoemail = "git config user.email \"kauamarcondes002@email.com\""
os.system(comandoemail)


comando1 = "git add *"
os.system(comando1)

mensagem = input("Digite a mensagem do commit: ")
while(len(mensagem) < 5):
    mensagem = input("Digite a mensagem do commit 🤬😡:  ")

comando2 = f"git commit -m {mensagem}"
os.system(comando2)

comando3 = "git push"
os.system(comando3)
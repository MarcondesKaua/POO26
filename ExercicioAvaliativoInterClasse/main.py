from classes import Jogadores, Equipes

def exibir_menu():
    print("\n" + "="*40)
    print("   CAMPEONATO INTERCLASSE DE E-SPORTS")
    print("="*40)
    print("1. Cadastrar jogador")
    print("2. Cadastrar equipe")
    print("3. Adicionar jogador a uma equipe")
    print("4. Listar todas as equipes")
    print("5. Listar jogadores de uma equipe")
    print("6. Buscar jogador por nickname")
    print("0. Sair")
    print("="*40)


list_jogadores = []
list_equipes = []

j1 = Jogadores()
j1.nome = "Coisa"
j1.nickname = "Coisinha"
j2 = Jogadores()
j2.nome = "Coiso"

c1 = Equipes()
c1.nome = "Coisadinha"

list_jogadores.append(j1)
list_jogadores.append(j2)
c1.cadastrar_jogador(j1)
list_equipes.append(c1)


while (True):
    exibir_menu()
    try:
        resp = int(input("Opção: "))
    except:
        print("Digita número nego")
        continue
    
    if resp == 1:
        jogador = Jogadores()
        jogador.preencher_info()
        list_jogadores.append(jogador)
    
    elif resp == 2:
        equipe = Equipes()
        equipe.preencher_info(list_jogadores)
        list_equipes.append(equipe)

    elif resp == 3:
        if(len(list_jogadores)> 0 and len(list_equipes) > 0):

            for i in range(len(list_equipes)):
                print(f"{i+1} - {list_equipes[i].nome}")

            id_equipe = int(input("Qual a equipe vc quer: "))

            for i in range(len(list_jogadores)):
                print(f"{i+1} - {list_jogadores[i].nome}")
            
            id_jogador = int(input("Qual o jogador vc quer: "))

            try:
                list_equipes[id_equipe-1].cadastrar_jogador(list_jogadores[id_jogador-1])
            except:
                print("Deu algumn erro")
        else: 
            print("Nao há jogadores nem equipes suficientes")

    elif resp == 4:
        for e in list_equipes:
            e.apresentar_equipe()
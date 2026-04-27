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
c1.nome = "Coisadinhas"

list_jogadores.append(j1)
list_jogadores.append(j2)
c1.cadastrar_jogador(j1, list_equipes)
list_equipes.append(c1)


while (True):
    exibir_menu()
    try:
        resp = int(input("Opção: "))
    except:
        print("Digita número")
        continue
    
    if resp == 1:
        jogador = Jogadores()
        jogador.preencher_info(list_jogadores)
        list_jogadores.append(jogador)
    
    elif resp == 2:
        equipe = Equipes()
        equipe.preencher_info()
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
                list_equipes[id_equipe-1].cadastrar_jogador(list_jogadores[id_jogador-1], list_equipes)
            except:
                print("Deu algum erro")
        else: 
            print("Nao há jogadores nem equipes suficientes")

    elif resp == 4:
        for e in list_equipes:
            print(f"Equipe {e.apresentar_equipe()}")
    
    elif resp == 5:
        if(len(list_equipes) > 0):
            for i in range(len(list_equipes)):
                print(f"{i+1} - {list_equipes[i].nome}")

            try:
                id_equipe = int(input("Qual a equipe vc quer: "))
                if 0 <= id_equipe-1 < len(list_equipes):
                    equipe_selecionada = list_equipes[id_equipe-1]
                    equipe_selecionada.apresentar_jogadores_equipe()
            except:
                print("Algum erro")
    elif resp == 6:
        encontrado = False
        nick_procurando = input("Digite o nickname do jogador: ").strip()   
        if(len(list_jogadores) > 0):
            for i in list_jogadores:
                if i.nickname.lower() == nick_procurando.lower():
                    print("Jogador: ")
                    print(i.apresentar())
                    encontrado = True
                    break
            if not encontrado:
                print("Nenhum jogador com esse nick encontrado")
    elif resp == 0:
        print("Saindo do programa")
        break
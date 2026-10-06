# Script de teste: roda o CRUD completo SEM abrir o jogo.
# Se algo der errado aqui, o problema é no banco — não no Arcade.
from banco import db, Pontuacao, inicializar_banco, buscar_top10

# 1. Garante que o arquivo ranking.db e a tabela existem
inicializar_banco()

# 2. CREATE: salva algumas partidas de teste
Pontuacao.create(nome_jogador="Rafael", pontos=480, tempo_partida=62.4)
Pontuacao.create(nome_jogador="Ana", pontos=350, tempo_partida=58.1)
Pontuacao.create(nome_jogador="Carol", pontos=610, tempo_partida=70.0)
Pontuacao.create(nome_jogador="teste", pontos=3, tempo_partida=5.0)

# 3. READ: quantos registros existem e quem está no topo
print(f"Total de partidas salvas: {Pontuacao.select().count()}")

print("\n--- TOP 10 ---")
for posicao, p in enumerate(buscar_top10(), start=1):
    print(f"{posicao}º - {p}")

# 4. UPDATE: corrige o nome de um jogador
ana = Pontuacao.get_or_none(Pontuacao.nome_jogador == "Ana")
if ana:
    ana.nome_jogador = "Ana Paula"
    ana.save()
    print(f"\nAtualizado: {ana}")

# 5. DELETE: confere antes com select() e só depois apaga
alvos = Pontuacao.select().where(Pontuacao.pontos < 10)
print(f"\nSerão apagados {alvos.count()} registro(s):")
for p in alvos:
    print(f"  {p}")

apagados = Pontuacao.delete().where(Pontuacao.pontos < 10).execute()
print(f"Registros apagados: {apagados}")

# 6. Fecha a conexão ao terminar
db.close()

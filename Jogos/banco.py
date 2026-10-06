import datetime                   # Para registrar data e hora de cada partida
from peewee import *              # Traz SqliteDatabase, Model e os tipos de campo

# ==========================================
# CONEXÃO COM O BANCO DE DADOS
# ==========================================
# O arquivo ranking.db é criado automaticamente na pasta do projeto
# na primeira vez que o banco for usado
db = SqliteDatabase("ranking.db")


# ==========================================
# CLASSE BASE DOS MODELOS
# ==========================================
class BaseModel(Model):
    """Classe mãe de todas as tabelas: define em qual banco elas moram."""

    class Meta:
        database = db


# ==========================================
# MODELO PONTUACAO (TABELA DO RANKING)
# ==========================================
class Pontuacao(BaseModel):
    """Cada objeto Pontuacao é uma partida salva no ranking."""

    nome_jogador = CharField()        # Quem jogou
    pontos = IntegerField()           # Resultado da partida
    tempo_partida = FloatField()      # Duração em segundos
    # Sem parênteses em "now": o Peewee chama a função no momento da criação
    data_hora = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"{self.nome_jogador} - {self.pontos} pts ({self.tempo_partida:.1f}s)"


# ==========================================
# FUNÇÕES DE APOIO
# ==========================================
def inicializar_banco():
    """Abre a conexão e cria as tabelas que ainda não existem."""
    db.connect(reuse_if_open=True)    # Não gera erro se já estiver conectado
    db.create_tables([Pontuacao])     # Não faz nada se a tabela já existir


def buscar_top10():
    """Devolve as 10 melhores pontuações; em caso de empate, vence o mais rápido."""
    consulta = (Pontuacao
                .select()
                .order_by(Pontuacao.pontos.desc(), Pontuacao.tempo_partida.asc())
                .limit(10))
    # list() executa a consulta agora e guarda o resultado na memória
    return list(consulta)

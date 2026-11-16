"""Camada de persistência: mapeamento objeto-relacional com Peewee (SQLite)."""
import datetime

from peewee import CharField, DateTimeField, FloatField, IntegerField, Model, SqliteDatabase

from .config import ARQUIVO_BANCO

db = SqliteDatabase(ARQUIVO_BANCO)


class BaseModel(Model):
    """Classe base: todos os modelos usam o mesmo banco (ranking.db)."""

    class Meta:
        database = db


class Pontuacao(BaseModel):
    nome_jogador = CharField()
    pontos = IntegerField()
    tempo_partida = FloatField()
    data_hora = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"{self.nome_jogador} - {self.pontos} pts ({self.tempo_partida:.1f}s)"


def iniciar_banco():
    """Abre a conexão e cria a tabela caso ainda não exista."""
    db.connect(reuse_if_open=True)
    db.create_tables([Pontuacao], safe=True)

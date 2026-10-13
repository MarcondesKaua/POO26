from datetime import datetime

from peewee import (
    SqliteDatabase, Model, CharField, IntegerField, FloatField, DateTimeField
)

db = SqliteDatabase("ranking.db")


class Pontuacao(Model):
    nome_jogador = CharField(max_length=12)
    pontos = IntegerField()
    tempo_partida = FloatField()
    data_hora = DateTimeField(default=datetime.now)

    class Meta:
        database = db


def inicializar_banco():
    """Abre a conexão e garante que a tabela exista."""
    db.connect(reuse_if_open=True)
    db.create_tables([Pontuacao])


def buscar_top10():
    """Mais pontos primeiro; em caso de empate, vence quem foi mais rápido."""
    consulta = (
        Pontuacao.select()
        .order_by(Pontuacao.pontos.desc(), Pontuacao.tempo_partida.asc())
        .limit(10)
    )
    return list(consulta)
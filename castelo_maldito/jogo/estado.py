"""Estado da partida que atravessa as fases (vidas, pontos, equipamento...)."""

MAX_SUBS = 2   # quantidade de slots de sub-arma


class Progresso:
    def __init__(self):
        self.vidas = 3
        self.vida_max = 12
        self.vida = 12
        self.coracoes = 5
        self.pontos = 0
        self.tempo = 0.0  # segundos jogados (vira tempo_partida no ranking)
        self.armas = [0]  # índices (em armas.ARMAS) já conquistados
        self.arma_atual = 0
        self.subs = []       # sub-armas guardadas (até MAX_SUBS): 'adaga', 'machado', 'agua', 'bumerangue'
        self.sub_atual = 0   # índice do slot que está "na mão"
        self.fase = 0
        self.mortes = 0
        self.abates = 0
        self.venceu = False

    @property
    def sub(self):
        """Sub-arma que está na mão (ou None se não houver nenhuma)."""
        return self.subs[self.sub_atual] if self.subs else None

    def pegar_sub(self, nome):
        """Guarda uma sub-arma recém-pega.

        Slot livre  -> guarda e equipa a nova; retorna None.
        Slots cheios -> a nova entra no lugar da que está na mão; retorna o nome da que foi largada.
        """
        if len(self.subs) < MAX_SUBS:
            self.subs.append(nome)
            self.sub_atual = len(self.subs) - 1
            return None
        largada = self.subs[self.sub_atual]
        self.subs[self.sub_atual] = nome
        return largada

    def trocar_sub(self):
        """Alterna a sub-arma da mão entre os slots ocupados. Retorna True se trocou."""
        if len(self.subs) > 1:
            self.sub_atual = (self.sub_atual + 1) % len(self.subs)
            return True
        return False

    def bonus_final(self):
        """Bônus somado ao término com vitória."""
        return self.vidas * 500 + (self.vida * 50)

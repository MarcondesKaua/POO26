class Pedido:
    def __init__(self, produto, quantidade, preco_unitario):
        self.produto = produto
        self.quantidade = quantidade 
        self.preco_unitario = preco_unitario
    
    def descrever(self):
        print (f"PEDIDO: {self.produto} X {self.quantidade} -Total: {self.quantidade * self.preco_unitario} R$")

ped = Pedido("Zotesso", 2, 0.5)
ped.descrever()
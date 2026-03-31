class Conta_bancaria:

    
    def __init__(self, numero, titular, saldo): 
        self.numero_conta = numero
        self.titular = titular
        self.saldo = saldo

    def sacar_dinheiro(self, valor):
        if self.saldo >= valor: 
            self.saldo -= valor
            print(f"Saque realizado com sucesso, novo saldo {self.saldo}")
            return True
        else:
            print(f"Saldo insuficiente para saque! Saldo atual de {self.titular}: R$ {self.saldo:.2f}")
            return False
            
    def depositar_dinheiro(self, valor):
        self.saldo += valor
        print(f"Deposito realizado com sucesso, novo saldo {self.saldo}")

    def transferir_dinheiro(self, valor, conta_destino):
        if self.sacar_dinheiro(valor):
            conta_destino.depositar_dinheiro(valor)
       
            print(f"Transferência realizada com sucesso!")
            print(f"Saldo de {self.titular}: R$ {self.saldo:.2f}")
            print(f"Saldo de {conta_destino.titular}: R$ {conta_destino.saldo:.2f}")

conta1 = Conta_bancaria(1, "João", 1000.0)
conta2 = Conta_bancaria(2, "Maria", 500.0)

print("TESTE")
conta1.depositar_dinheiro(200) 
conta2.sacar_dinheiro(300) 
conta1.transferir_dinheiro(400, conta2)
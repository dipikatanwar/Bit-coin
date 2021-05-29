from Helper import Helper
class TrxInput():
    def __init__(self,transactionOutputId, outputTx):
        self.transactionOutputId = transactionOutputId
        self.outputTx = outputTx

class TrxOutput():
    def __init__(self,recepient,amount, trxId):
        self.recepient = recepient
        self.amount = amount
        self.trxId = trxId
        self.id = Helper.getHash(str(self.recepient) + str(self.amount) + str(self.trxId))
from time import time
from Config import *
from Helper import Helper
from UTXO import TrxInput, TrxOutput
from MarkelTree import MarkelTree
from Transaction import Transaction
from Block import Block

class BlockChain():
    def __init__(self, public_key):
        self.pendingTransaction = []
        self.UTXO = {}
        self.chain = [self.createGenesisBlock(public_key, 1000)]

    def createGenesisBlock(self, public_key, amount):
        data = {
            'senderAddr':'SYSTEM',
            'receiverAddr':public_key,
            'amount': amount,
        }
        t = Transaction(data)
        block = Block(time(),[t], 0)
        block.mineBlock()
        o = TrxOutput(public_key, amount, t.hash)
        self.UTXO[o.id] = o 
        return block

    def insertPendingTransaction(self, minerAddress):
        if len(self.pendingTransaction) == 0: return
        data = {}
        data['senderAddr'] = 'SYSTEM'
        data['receiverAddr'] = minerAddress
        data['amount'] = MINING_REWARD

        self.performTransaction(Transaction(data))
        block = Block(time(), self.pendingTransaction, self.getLastBlock().hash)
        block.mineBlock()
        self.chain.append(block)
        self.pendingTransaction = []

    
    def createBlock(self, minerAddress):
        if len(self.pendingTransaction) == 0: return None
        data = {}
        data['senderAddr'] = 'SYSTEM'
        data['receiverAddr'] = minerAddress
        data['amount'] = MINING_REWARD
        if not self.performTransaction(Transaction(data)): return None
        block = Block(time(), self.pendingTransaction, self.getLastBlock().hash)
        block.mineBlock()
        return block
    
    def appendBlock(self, block):      
        if not block.verifyPOW(): return False
        if block.prevHash != self.getLastBlock().hash: return False
        if not block.hasAllTransactionValid():return False

        for trx in block.transactions:
            if trx in self.pendingTransaction:
                self.pendingTransaction.remove(trx)
        self.chain.append(block)
        return True

    def getLastBlock(self):
        return self.chain[-1]

    def isChainValid(self):
        totalBlocks = len(self.chain)
        preHash = self.chain[0].hash
        for i in range(1,totalBlocks):
            block = self.chain[i]
            if not block.hasAllTransactionValid():
                print("all tx not valid")
                return False
            if block.calculateHash() != block.hash:
                print("hash not same")
                return False
            if block.prevHash != preHash:
                print("privious hash error")
                return False
            if block.hash[:block.prof_of_work_zeros] != "0"*block.prof_of_work_zeros:
                return False
            preHash = block.hash
        return True
            
    def performTransaction(self, tra):
        if not self.processTrx(tra):
            print("fail")
            return False
        self.pendingTransaction.append(tra)
        return True

    def processTrx(self, trx):
        if trx==None or trx.data['senderAddr'] =='' or trx.data['receiverAddr'] =='':
            print('A Transaction must have sender and receiver Address')
            return False

        senderAddr, receiverAddr, amount = trx.data['senderAddr'], trx.data['receiverAddr'], trx.data['amount']
        if not trx.varifySign():
            print('sign')
            return False

        if senderAddr != 'SYSTEM':
            inputUnspent = trx.getInputsValue()
            if inputUnspent < amount:return False
            leftOver = inputUnspent - amount
            trx.outputTrxList.append(TrxOutput(senderAddr, leftOver, trx.calculateHash()))

        trx.outputTrxList.append(TrxOutput(receiverAddr, amount, trx.calculateHash()))
        for o in trx.outputTrxList:self.UTXO[o.id] = o
        for i in trx.inputTrxList:
            if self.UTXO.get(i.transactionOutputId, 0) != 0:
                del self.UTXO[i.transactionOutputId]

        return True

    def size(self):
        sz = 0
        for block in self.chain:
            sz += block.size()
        return sz
        
    def printChain(self):
        for block in self.chain:
            print('--------------------')
            print(block.prevHash, " ", block.hash, " ", block.nonce, " ", block.calculateHash())

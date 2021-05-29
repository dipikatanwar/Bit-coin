from Helper import Helper
from time import time
import sys

class Transaction():
    def __init__(self, data, inputTrxList=[], private_key = None):
        self.data = data
        self.signature = ''
        self.created_at = time()
        self.hash = Helper.getHash(self.toString())
        self.inputTrxList = inputTrxList
        self.outputTrxList = []
        if private_key:self.sign(private_key)
    
    def size(self):
        sz = 0
        for item in [self.data, self.signature, self.created_at, self.hash, self.inputTrxList, self.outputTrxList]:
            sz += sys.getsizeof(item)
        return sz

    def calculateHash(self):
        return Helper.getHash(self.toString())
    
    def sign(self, key):
        if self.data['senderAddr'] == 'SYSTEM':return
        self.signature = Helper.sign(self.toString(), key)
        
    def isValid(self):
        if self.data['senderAddr'] == 'SYSTEM': return True
        if self.signature == '': return False
        return Helper.verify(self.toString(), self.data['senderAddr'], self.signature)

    def varifySign(self):
        if self.data['senderAddr'] == 'SYSTEM': return True
        if self.signature == '': return False
        return Helper.verify(self.toString(), self.data['senderAddr'], self.signature)

    def getInputsValue(self):
        total = 0
        for i in self.inputTrxList:
            if not i.outputTx: continue
            total += i.outputTx.amount
        return total

    def getOutputsValue(self):
        total = 0
        for o in self.outputTrxList:
            total += o.amount
        return total

    def toString(self):
        return str(self.data) + str(self.created_at)

    def __str__(self): 
        return self.toString()
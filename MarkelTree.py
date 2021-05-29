from Helper import Helper
import copy
from Config import *
import sys

class MarkelTree():
    def __init__(self, transactionList, arrity = MARKEL_TREE_ARITY):
        self.transactions = copy.deepcopy(transactionList)
        self.arrity = arrity
        hashOfLeaf = [t.hash for t in transactionList]
        self.hashTree = self.createMarkelTree(hashOfLeaf)
    
    def createMarkelTree(self, hashOfLeaf):
        tree = []
        while True:
            L = len(hashOfLeaf)
            if L==1:
                tree.append(hashOfLeaf)
                break
            rem = L % self.arrity
            if rem != 0:
                L += (self.arrity - rem)
                hashOfLeaf += hashOfLeaf[-1:]*(self.arrity - rem)
            tree.append(hashOfLeaf)
            hashOfLeaf = [Helper.getHash(''.join(hashOfLeaf[i:i+self.arrity])) for i in range(0, L, self.arrity)]
        return tree
    
    def varifyTransactions(self, transactions):
        hashOfLeaf = [t.hash for t in transactions]
        tree = self.createMarkelTree(hashOfLeaf)
        ret = (self.hashTree[-1][0] == tree[-1][0])
        return ret
    
    def size(self):
        sz = 0
        for item in self.hashTree:
            sz += sys.getsizeof(item)
        return sz
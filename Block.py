from Helper import Helper
import copy
from Config import *
from MarkelTree import MarkelTree
import sys

class Block():
    def __init__(self, timestamp, transactions, preHash):
        self.timestamp = timestamp
        self.transactions = copy.deepcopy(transactions)
        self.nonce = 0
        self.prevHash = preHash
        self.prof_of_work_zeros = PROF_OF_WORK_ZEROS
        self.markelTree = MarkelTree(self.transactions)
        self.markelRoot = self.markelTree.hashTree[-1][0]
        self.hash = self.calculateHash()

    def size(self):
        sz = 0
        for item in [self.timestamp, self.nonce, self.prevHash, self.hash, self.prof_of_work_zeros, self.markelRoot]:
            sz += sys.getsizeof(item)
        for t in self.transactions:
            sz += t.size()
        sz += self.markelTree.size()
        return sz

    def calculateHash(self):
        s = str(self.timestamp) + str(self.prevHash) + str(self.nonce) + self.markelTree.hashTree[-1][0]
        return Helper.getHash(s)
    
    def mineBlock(self):
        while True:
            if(self.hash[:self.prof_of_work_zeros] == "0"*self.prof_of_work_zeros):break
            self.nonce += 1
            self.hash = self.calculateHash()
        
    def hasAllTransactionValid(self):
        for t in self.transactions:
            if not t.isValid():return False
        if not self.markelTree.varifyTransactions(self.transactions):return False
        return True
    
    def verifyPOW(self):
        return self.hash[:self.prof_of_work_zeros] == "0"*self.prof_of_work_zeros
    

    def size(self):
        size_byte = 0
        for item in [self.block_type,self.previous_block_hash,self.index,self.pow_number_of_zeros,self.hash_type,self.merkle_tree_root, self.block_hash,self.nounce]:
            size_byte += sys.getsizeof(item)
        return size_byte

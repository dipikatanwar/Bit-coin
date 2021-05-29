from Helper import Helper
from time import sleep,time
from collections import deque
import threading
import copy
from Config import *
from BlockChain import *
import random

class Node():
    def __init__(self, nodeId, totalNodes):
        self.nodeId = nodeId
        self.totalNodes = totalNodes
        self.rsaKey, self.private_key, self.public_key = Helper.rasKeys()
        self.startTime = time()
        self.receiveQueue = deque()
        self.receiveQueueLock = threading.Lock()
        self.publicKeyList = {}
        self.lastTrasactionVarified = True



    def receiveBlockChain(self, blockChain):
        self.blockChain = copy.deepcopy(blockChain) 

    def printUTXO(self):
        for v in self.blockChain.UTXO.values():
            print(nodePublicKeyToId[v.recepient], ' ', v.amount)

    def getBalance(self):
        balance = 0
        for _,value in self.blockChain.UTXO.items():
            if value.recepient == self.public_key:
                balance += value.amount
        return balance

    def sendFunds(self, recepient, amount):
        if self.getBalance() < amount: return None
        inputUTXO = []
        total = 0
        for key,value in self.blockChain.UTXO.items():
            if value.recepient == self.public_key:
                total += value.amount
                inputUTXO.append(TrxInput(key, value))
            if total > amount:break

        data = {
            'senderAddr': self.public_key,
            'receiverAddr': recepient,
            'amount': amount
        }

        trx = Transaction(data, inputUTXO)
        trx.sign(self.private_key)


        # self.blockChain.removeUTXO([inUTXO.transactionOutputId for inUTXO in inputUTXO])

        return trx

    def receive(self, poleTime):
        ret, msgType, data = False, None, None
        self.receiveQueueLock.acquire()
        start_time = time()
        while (time() - start_time) < poleTime:
            try:
                msgType, data = self.receiveQueue.popleft()
                ret = True
                break
            except Exception as _:
                pass    
        self.receiveQueueLock.release()
        return ret, msgType, data

    def sendMessage(self, msgType, dest, data):
        dest.receiveQueueLock.acquire()
        dest.receiveQueue.append((msgType,data))
        dest.receiveQueueLock.release()

    
    def work(self):
        print("Balance of Node id ", self.nodeId,' = ', self.getBalance())
        timeWaited = 0
        poleTime = 1
        working  = True
        lastBlockCreatedTime = lastTrasactionTime = time()
        while working:
            ret, msgType,trx = self.receive(poleTime)
            if ret:
                #receive block within poleTime
                trx = copy.deepcopy(trx)
                timeWaited = 0
                if msgType == MSG.PERFORM_TRX:
                    self.blockChain.performTransaction(trx)
                    # print('[TRX RECEIVED-{}]'.format(str(self.nodeId)))
                elif msgType == MSG.RECEIVE_BLOCK:
                    # print('[BLOCK RECEIVED-{}]'.format(str(self.nodeId)))
                    self.blockChain.appendBlock(trx)
                    lastBlockCreatedTime = time()
                else:
                    print('[INVALID MSG RECEIVED-{}]'.format(str(self.nodeId)))
            else:
                #receive block after poletime
                # self.blockChain.isChainValid()
                # print("Integrity ", self.nodeId, self.blockChain.isChainValid())
                timeWaited += poleTime
                if timeWaited >= SIMULATION_TIME:
                    working = False
                else:
                    if time() - lastTrasactionTime > WAIT_BEFORE_NEW_TRX and self.lastTrasactionVarified:
                        if Helper.isMyTurn(self.nodeId, self.totalNodes):
                            receiver = Helper.pickReceiver(self.nodeId, self.totalNodes)
                            balance = self.getBalance()
                            if balance > 0:
                                lastTrasactionTime = time()
                                transfer_amount = random.randint(1, balance)
                                print('Transaction between Node ', self.nodeId,'( balance ', balance ,') and ', receiver, " of ", transfer_amount)
                                trx = self.sendFunds(nodeInfo[receiver].public_key, transfer_amount)
                                if trx:
                                    for i in range(self.totalNodes):
                                        if i!=self.nodeId:
                                            self.sendMessage(MSG.PERFORM_TRX, nodeInfo[i], trx)

                                    self.blockChain.performTransaction(trx)
                                    timeWaited = 0
                                    
                    if (time() - lastBlockCreatedTime) > BLOCK_CREATION_TIME:
                        if Helper.isMyTurn(self.nodeId, self.totalNodes):
                            for t in self.blockChain.pendingTransaction: t.data['amount']
                            block = self.blockChain.createBlock(self.public_key)
                            if block:
                                temp = []
                                addMyBlock = True
                                while True:
                                    ret, msgType,data = self.receive(poleTime)
                                    if not ret:
                                        break
                                    else:
                                        if msgType == MSG.RECEIVE_BLOCK:
                                            self.blockChain.appendBlock(data)
                                            addMyBlock = False
                                            break
                                        else:
                                            temp.append((msgType, data))
                                for msgType, data in temp:self.sendMessage(msgType, self, data)
                                if addMyBlock:
                                    print("MINNER address ", self.nodeId, " Reward given ", MINING_REWARD)
                                    for i in range(self.totalNodes):
                                        if i!=self.nodeId:
                                            self.sendMessage(MSG.RECEIVE_BLOCK, nodeInfo[i], block)
                                
                                    if not self.blockChain.appendBlock(block):
                                        pass

                                    lastBlockCreatedTime = time()
                                    timeWaited = 0
        print("balance of node ", self.nodeId, " ", self.blockChain.getBalance(self.public_key))
        
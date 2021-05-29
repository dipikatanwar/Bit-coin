from Config import *
from Node import Node
import threading
from BlockChain import BlockChain
from time import time


def run():
    blockChain = None
    threadPool = []
    for nodeId in range(TOTAL_NODES):
        node = Node(nodeId, TOTAL_NODES)
        if not blockChain:blockChain = BlockChain(node.public_key)
        node.receiveBlockChain(blockChain)
        nodeInfo[nodeId] = node
        nodePublicKeyToId[node.public_key] = nodeId

    for node in nodeInfo.values():
        t = threading.Thread(target=node.work, args=[], daemon=True)
        t.start()
        threadPool.append(t)
    
    # for t in threadPool:t.join()
    while True: pass

    print('Ending BlockChain Simulation')
    # print(nodeInfo.keys())

if __name__=='__main__':
    run()
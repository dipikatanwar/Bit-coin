from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256,SHA1,SHA224,SHA384,SHA512
from Crypto.Signature import PKCS1_v1_5
from Config import *
import random


class Helper():
    @staticmethod
    def getHash(string, method=CRYPTO_METHOD):
        h = method.new()
        h.update(bytes(string, encoding='utf8'))
        return h.hexdigest()

    @staticmethod
    def rasKeys(length=1024):
        key = RSA.generate(length)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return key, private_key, public_key

    @staticmethod
    def sign(message, key):
        key = RSA.import_key(key)
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(bytes(message, encoding='utf8'))
        sig = signer.sign(digest)
        return sig

    @staticmethod
    def verify(message, key, signature):
        key = RSA.import_key(key)
        digest = SHA256.new()
        digest.update(bytes(message, encoding='utf8'))
        verified = PKCS1_v1_5.new(key).verify(digest, signature)
        return verified
    
    @staticmethod
    def publishPublicKey(self, public_key):
        commonDataLock.acquire()
        if public_key not in nodePublicKeys:
            nodePublicKeys.append(public_key)
        commonDataLock.release()
    
    @staticmethod
    def pickReceiver(sender, totalNodes):
        while True:
            x = random.randint(0, totalNodes-1)
            if x != sender: return x
        
    @staticmethod
    def isMyTurn(nodeId, totalNodes):
        return nodeId == random.randint(0, totalNodes-1)

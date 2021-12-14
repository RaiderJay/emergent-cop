from time import time
import hashlib
import json
from config import Config

cf = Config()

class BlockChainCop(object):
    def __init__(self):
        self.chain = []
        self.pending_ko = []

        self.new_block(previous_hash="There is no previous hash!!!", proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_ko,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.pending_ko = []
        self.chain.append(block)

        return block

    @property
    def last_block(self):
        return self.chain[-1]

    def new_knowledge_object(self, type, origin, radius, distance):
        knowledge = {
            'type': type,
            'origin': origin,
            'radius': radius,
            'distance': distance,
        }
        self.pending_ko.append(knowledge)
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        string_object = json.dumps(block, sort_keys=True)
        block_string = string_object.encode()

        raw_hash = hashlib.sha256(block_string)
        hex_hash = raw_hash.hexdigest()

        return hex_hash


#blockchain = BlockChainCop()
#t1 = blockchain.new_knowledge_object(cf.thermal, (300, 200), 30, 300)
#t2 = blockchain.new_knowledge_object(cf.thermal, (300, 200), 30, 300)
#t3 = blockchain.new_knowledge_object(cf.thermal, (300, 200), 30, 300)
#blockchain.new_block(12345)

##t5 = blockchain.new_knowledge_object(cf.thermal, (300, 200), 30, 300)
#t6 = blockchain.new_knowledge_object(cf.thermal, (300, 200), 30, 300)
#blockchain.new_block(6789)

#print("Genesis block: ", blockchain.chain)
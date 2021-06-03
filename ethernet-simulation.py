import simpy
import math
import numpy as np
import matplotlib.pyplot as plt
import random
import sys


class G:
    RANDOM_SEED = 33
    SIM_TIME = 1000000
    SLOT_TIME = 1
    N = int(sys.argv[1])
    RETRANMISSION_POLICIES = []
    RETRANMISSION_POLICIES.append(str(sys.argv[2]))
    ARRIVAL_RATES = []
    ARRIVAL_RATES.append(float(sys.argv[3]))
    LONG_SLEEP_TIMER = 1000000000
    SUCCESS = 0


# Server process responsible for handling and detecting retransmission policies
class Server_Process(object):
    def __init__(self, env, dictionary_of_nodes, retran_policy, slot_stat):
        self.env = env
        self.dictionary_of_nodes = dictionary_of_nodes 
        self.retran_policy = retran_policy 
        self.slot_stat = slot_stat
        self.current_slot = 0
        self.action = env.process(self.run())
        self.retransmit = 0
            
    def run(self):
        while True: 
            yield self.env.timeout(1)
            self.current_slot += 1

            # Check for collision
            for i in list(range(1,G.N+1)):
                if self.dictionary_of_nodes[i].nextSlot == self.current_slot:
                    self.retransmit +=1

            # If there is collision
            if self.retransmit >= 2:
                for i in list(range(1,G.N+1)):
                    if self.dictionary_of_nodes[i].nextSlot == self.current_slot:
                        self.dictionary_of_nodes[i].retrans_attempt =  self.dictionary_of_nodes[i].retrans_attempt + 1
                        # Retransmission policies
                        if(G.RETRANMISSION_POLICIES[0] =="pp"):
                            nextSlot = self.current_slot
                            while True:
                                nextSlot += 1
                                if random.choice([0, 1]) == 1:
                                    self.dictionary_of_nodes[i].nextSlot = nextSlot
                                    break
                                else:
                                    continue
                        if(G.RETRANMISSION_POLICIES[0] =="op"):
                            nextSlot = self.current_slot
                            while True:
                                nextSlot += 1
                                chance = random.random()
                                chance2 = float(chance)
                                prob = 1 / G.N
                                if prob > chance2:
                                    self.dictionary_of_nodes[i].nextSlot = nextSlot
                                    break
                                else:
                                    continue
                        if(G.RETRANMISSION_POLICIES[0] == "lb"):
                            high = min(self.dictionary_of_nodes[i].retrans_attempt + 1, 1024)
                            nextSlot = np.random.randint(0, high)
                            self.dictionary_of_nodes[i].nextSlot = self.current_slot  + 1 + nextSlot
                        if(G.RETRANMISSION_POLICIES[0] == "beb"):
                            high = min(10,self.dictionary_of_nodes[i].retrans_attempt)
                            high2 = pow(2, high)
                            nextSlot = np.random.randint(0, high2)
                            self.dictionary_of_nodes[i].nextSlot = self.current_slot + 1 + nextSlot

            # Successful transmission
            else:
                for i in list(range(1,G.N+1)):
                    if self.dictionary_of_nodes[i].nextSlot == self.current_slot:
                        G.SUCCESS += 1
                        # Reset all needed state values for given node
                        self.dictionary_of_nodes[i].nextSlot = 0
                        self.dictionary_of_nodes[i].retrans_attempt = 0
                        self.dictionary_of_nodes[i].queue.pop()
                        # Update nextslot if more nodes in queue
                        if len(self.dictionary_of_nodes[i].queue) >= 1:
                            self.dictionary_of_nodes[i].nextSlot = self.current_slot+1
            self.retransmit = 0
  

                    
# Node proccess class, just responsible for generating packets    
class Node_Process(object): 
    def __init__(self, env, id, arrival_rate):
        
        self.env = env
        self.id = id
        self.arrival_rate = arrival_rate
        self.nextSlot = 0
        self.action = env.process(self.run())
        self.retrans_attempt = 0
        self.queue = []
        
    def run(self):
        while True:
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            # If statement detects if first packet still needs to be retransmitted.
            if self.nextSlot > self.env.now:
                arrival_time = self.env.now  
                new_packet = Packet(self.id, arrival_time)
                self.queue.append(new_packet)
                continue
            # Generate packet 
            arrival_time = self.env.now  
            new_packet = Packet(self.id, arrival_time)
            self.queue.append(new_packet)
            self.nextSlot = math.ceil(self.env.now)
        
class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time


class StatObject(object):    
    def __init__(self):
        self.dataset =[]

    def addNumber(self,x):
        self.dataset.append(x)


def main():
    random.seed(G.RANDOM_SEED)

    for retran_policy in G.RETRANMISSION_POLICIES: 
        for arrival_rate in G.ARRIVAL_RATES:
            env = simpy.Environment()
            slot_stat = StatObject()
            dictionary_of_nodes  = {} 
            
            for i in list(range(1,G.N+1)):
                node = Node_Process(env, i, arrival_rate)
                dictionary_of_nodes[i] = node
            server_process = Server_Process(env, dictionary_of_nodes,retran_policy,slot_stat)
            env.run(until=G.SIM_TIME)

            if G.SUCCESS == 0:
                ans = 0
            else:
                ans = G.SUCCESS / G.SIM_TIME
            format_float = "{:.2f}".format(ans)
            print(format_float)
            G.SUCCESS = 0

    
if __name__ == '__main__': main()

"""
Created on Thu Mar 10 11:15:41 2022

@author: CLARA PÉREZ ESTEBAN
"""
from multiprocessing import Condition, Lock
from multiprocessing import Value

class Table():
    def __init__(self, nphil, manager):
        self.phil = manager.list([False]*nphil)
        self.numphil = nphil
        self.current_phil = None
        self.eating = Value('i',0)
        self.mutex = Lock()
        self.freefork = Condition(self.mutex)
        
    def set_current_phil(self, i):
        self.current_phil = i
    
    def phils_not_eating(self):
        return not(self.phil[(self.current_phil-1)%(self.numphil)]) and \
            not(self.phil[(self.current_phil+1)%(self.numphil)])
        
    def wants_eat(self,i):
        self.mutex.acquire()
        self.freefork.wait_for(self.phils_not_eating)
        self.phil[i] = True
        self.eating.value += 1
        self.mutex.release()
    
    def wants_think(self,i):
        self.mutex.acquire()
        self.phil[i] = False
        self.eating.value -= 1
        self.freefork.notify_all()
        self.mutex.release()

class AnticheatTable():
    def __init__(self, nphil, manager):
        self.phil = manager.list([False]*nphil)
        self.numphil = nphil
        self.current_phil = None
        self.eating = Value('i',0)
        self.hungry = manager.list([False]*nphil)
        self.mutex = Lock()
        self.freefork = Condition(self.mutex)
        self.chungry = Condition(self.mutex)
        
    def set_current_phil(self, i):
        self.current_phil = i
        
    def next_not_hungry(self):
        return not(self.hungry[(self.current_phil+1)%(self.numphil)])
    
    def phils_not_eating(self):
        return not(self.phil[(self.current_phil-1)%(self.numphil)]) and \
            not(self.phil[(self.current_phil+1)%(self.numphil)])
        
    def wants_eat(self,i):
        self.mutex.acquire()
        self.chungry.wait_for(self.next_not_hungry)
        self.hungry[i] = True
        self.freefork.wait_for(self.phils_not_eating)
        self.phil[i] = True
        self.eating.value += 1
        self.hungry[i] = False
        self.chungry.notify_all()
        self.mutex.release()
    
    def wants_think(self,i):
        self.mutex.acquire()
        self.phil[i] = False
        self.eating.value -= 1
        self.freefork.notify_all()
        self.mutex.release()
        
class CheatMonitor():
    def __init__(self):
        self.cheatmate0_eating = Value('b',False)
        self.cheatmate2_eating = Value('b',False)
        self.mutex = Lock()
        self.cheating = Condition(self.mutex)
        
    def cheater_eating(self):
        return self.cheatmate0_eating.value and self.cheatmate2_eating.value
        
    def is_eating(self,i):
        self.mutex.acquire()
        if i == 0:
            self.cheatmate0_eating.value = True
        elif i == 2:
            self.cheatmate2_eating.value = True
        self.cheating.notify_all()
        self.mutex.release()
    
    def wants_think(self,i):
        self.mutex.acquire()
        self.cheating.wait_for(self.cheater_eating)
        if i == 0:
            self.cheatmate0_eating.value = False
        elif i == 2:
            self.cheatmate2_eating.value = False
        self.cheating.notify_all()
        self.mutex.release()
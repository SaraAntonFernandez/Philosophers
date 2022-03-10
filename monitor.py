from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Array, Manager, Value
import time
import random

class Table():
	def __init__(self, NPHIL, manager):
		self.mutex = Lock()
		self.NPHIL = NPHIL
		self.freefork = Condition(self.mutex)
		self.chungry = Condition(self.mutex)
		self.n_eating = Value('i', 0)
		self.n_thinking = Value('i', 0)
		self.phil = Array('i', [False]*self.NPHIL) # False = no comen = si piensan
		# True = si comen = no piensan
		self.hungry = Array('i', [False]*self.NPHIL) # False = no tienen hambre
		# True = hambrientos = quieren ponerse a comer
		
	def set_current_phil(self, i):
		self.current_phil = i  # filosofo actual = i
	
	def freeleftrightforks(self):
		return not(self.phil[(self.current_phil-1)%self.NPHIL] or self.phil[(self.current_phil+1)%self.NPHIL]) # si ambos NO comen tienen los dos tenedores libres (los cojo a la vez)
		
	def change_hungry(self):
		return (not self.hungry[(self.current_phil+1)%self.NPHIL])
	
	def wants_eat(self, i):
		self.mutex.acquire()
		self.current_phil = i
		if self.hungry[i]:# estoy hambriento
			self.freefork.wait_for(self.freeleftrightforks) # espero hasta tener libres ambos tenedores
			self.hungry[i] = False # ya no estoy hambriento
			self.n_eating.value += 1 # como
			self.n_thinking.value -= 1 # dejo de pensar
		else: # me pongo a la cola de hambrientos
			self.chungry.wait_for(self.change_hungry)
			self.chungry.notify_all()
		self.mutex.release()
		
        	
	def wants_think(self, i):
		self.mutex.acquire()
		self.current_phil = i
		self.phil[i] = False
		self.freefork.notify_all()
		self.n_eating.value -= 1 # dejo de comer
		self.n_thinking.value += 1 # me pongo a pensar
		self.mutex.release()
		
		
################################################################################################################

class CheatMonitor():
	def __init__(self):



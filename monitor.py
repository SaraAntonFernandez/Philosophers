from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Array, Manager, Value
import time
import random


class Table():
	def __init__(self, NPHIL: int, manager):
		self.mutex = Lock()
		self.NPHIL = NPHIL
		self.current_phil = None
		self.freefork = Condition(self.mutex)
		self.n_eating = Value('i', 0)
		self.n_thinking = Value('i', 0)
		self.phil = Array('i', [False]*self.NPHIL) # False = no comen = si piensan
		# True = si comen = no piensan
		
	def set_current_phil(self, i):
		self.current_phil = i  # filosofo actual = i
	
	def freeleftrightforks(self):
		return not(self.phil[(self.current_phil - 1)%self.NPHIL] or self.phil[(self.current_phil + 1)%self.NPHIL]) # si ambos NO comen tienen los dos tenedores libres (los cojo a la vez)
		
	def wants_eat(self, i):
		self.mutex.acquire()
		self.current_phil = i
		self.freefork.wait_for(self.freeleftrightforks) # espero hasta tener libres ambos tenedores
		self.n_eating.value += 1 # como
		self.n_thinking.value -= 1 # dejo de pensar
		self.mutex.release()
		
	def wants_think(self, i):
		self.mutex.acquire()
		self.current_phil = i
		self.phil[i] = False
		self.freefork.notify_all()
		self.n_eating.value -= 1 # dejo de comer
		self.n_thinking.value += 1 # me pongo a pensar
		self.mutex.release()	
		
#-------------------------------------------------------------------------------------------------------------

class CheatMonitor():
	def __init__(self):  # REVISAR
		self.mutex = Lock()
		self.NPHIL = NPHIL
		self.current_phil = None
		self.freefork = Condition(self.mutex)
		self.cheating = Condition(self.mutex)
		self.n_eating = Value('i', 0)
		self.n_thinking = Value('i', 0)
		self.phil = Array('i', [False]*self.NPHIL) # comiendo = True
		
	def set_current_phil(self, i):
		self.current_phil = i
		
	def is_eating(self, i):
		self.mutex.acquire()
		self.current_phil = i
		self.phil[self.current_phil] = True
		self.mutex.release()
	
	def cheat(self):
		return self.phil[(self.current_phil + 1)%self.NPHIL]
		
	def wants_think(self, i): # Se alian i e i+2 para que i+1 no coma, así que hasta que i+2 no este comiendo, no deja i de comer
		self.mutex.acquire()
		self.current_phil = i
		self.cheating.wait_for(self.cheat)
		self.phil[self.current_phil] = False
		self.freefork.notify_all()
		self.n_eating.value -= 1 # dejo de comer
		self.n_thinking.value += 1 # me pongo a pensar
		self.mutex.release()
		
#--------------------------------------------------------------------------------------------------------------

class AnticheatTable():
	def __init__(self, NPHIL: int, manager):
		self.mutex = Lock()
		self.NPHIL = NPHIL
		self.current_phil = None
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
		if self.hungry[self.current_phil]:# estoy hambriento
			self.freefork.wait_for(self.freeleftrightforks) # espero hasta tener libres ambos tenedores
			self.hungry[self.current_phil] = False # ya no estoy hambriento
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

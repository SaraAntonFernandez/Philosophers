from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Array, Manager, Value
import time
import random


class Table():
	def __init__(self, NPHIL: int, manager):
		self.mutex = Lock()
		self.manager = manager
		self.NPHIL = NPHIL
		self.current_phil = None
		self.freefork = Condition(self.mutex)
		self.n_eating = Value('i', 0)
		self.n_thinking = Value('i', 0)
		self.phil = self.manager.list([False]*self.NPHIL) # False = no comen = si piensan
		# True = si comen = no piensan
		
	def set_current_phil(self, i):
		self.current_phil = i  # filosofo actual = i
	
	def freeleftrightforks(self):
		return not(self.phil[(self.current_phil - 1)%self.NPHIL] or self.phil[(self.current_phil + 1)%self.NPHIL]) # si ambos NO comen tienen los dos tenedores libres (los cojo a la vez)
		
	def wants_eat(self, i):
		self.mutex.acquire()
		self.current_phil = i
		self.freefork.wait_for(self.freeleftrightforks) # espero hasta tener libres ambos tenedores
		self.phil[self.current_phil] = True
		self.n_eating.value += 1 # como
		self.n_thinking.value -= 1 # dejo de pensar
		self.mutex.release()
		
	def wants_think(self, i):
		self.mutex.acquire()
		self.current_phil = i
		self.phil[self.current_phil] = False
		self.freefork.notify_all()
		self.n_eating.value -= 1 # dejo de comer
		self.n_thinking.value += 1 # me pongo a pensar
		self.mutex.release()	
		
#-------------------------------------------------------------------------------------------------------------

class CheatMonitor():
	def __init__(self):
		self.mutex = Lock()
		self.manager = Manager()
		self.cheating = Condition(self.mutex)
		self.cheaters = self.manager.list([False]*2) # los tramposos son phil_0 y phil_2
		
	def partner_is_eating(self): # mi compañero con el que hago trampas está comiendo
		if self.current_phil == 0:
			return self.cheaters[1]
		else:
			return self.cheaters[0]
		
	def set_current_phil(self, i):
		self.current_phil = i
		
	def is_eating(self, i):
		self.mutex.acquire()
		self.current_phil = i
		self.cheaters[self.current_phil // 2] = True
		self.cheating.notify_all()
		self.mutex.release()
	
		
	def wants_think(self, i): 
		self.mutex.acquire()
		self.current_phil = i
		self.cheating.wait_for(self.partner_is_eating)
		self.cheaters[self.current_phil // 2] = False
		self.mutex.release()
		
#--------------------------------------------------------------------------------------------------------------

class AnticheatTable():
	def __init__(self, NPHIL: int, manager):
		self.mutex = Lock()
		self.NPHIL = NPHIL
		self.manager = manager
		self.current_phil = None
		self.freefork = Condition(self.mutex)
		self.chungry = Condition(self.mutex)
		self.n_eating = Value('i', 0)
		self.n_thinking = Value('i', 0)
		self.phil =  self.manager.list([False]*self.NPHIL)# False = no comen = si piensan
		# True = si comen = no piensan
		self.hungry = self.manager.list([False]*self.NPHIL) # False = no tienen hambre
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
			#self.chungry.wait_for(self.change_hungry)
			self.hungry[self.current_phil] = True
			self.chungry.notify_all()
		self.mutex.release()
        	
	def wants_think(self, i):
		self.mutex.acquire()
		self.current_phil = i
		self.phil[self.current_phil] = False
		self.freefork.notify_all()
		self.n_eating.value -= 1 # dejo de comer
		self.n_thinking.value += 1 # me pongo a pensar
		self.mutex.release()

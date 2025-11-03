import random
import itertools
from collections import Counter

mapSuits = {0 : 'Hearts', 1 : 'Diamonds', 2 : 'Spades', 3 : 'Clubs'}
mapVals = {x : str(x + 2) for x in range(9)} | {9 : 'Jack', 10 : 'Queen', 11 : 'King', 12 : 'Ace'}

class Card:
	def __init__(self, s, v):
		self.suit = s
		self.value = v
	
	def __repr__(self):
		return f"{mapVals[self.value]} of {mapSuits[self.suit]}"

class Deck:
	def __init__(self):
		self.suits = [x for x in range(4)]
		self.vals = [x for x in range(13)]
		self.deck = [Card(x, y) for x in self.suits for y in self.vals]
	
	def shuffle(self):
		random.shuffle(self.deck)

def Player:
	def __init__(self, n, m):
		self.name = n
		self.money = money
	
	def new(self):
		self.hole = []

class Community:
	def __init__(self):
		self.cards = []
	
	def new(self):
		self.cards = []

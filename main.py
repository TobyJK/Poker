import random
import itertools
from collections import Counter

mapSuits = {0 : 'Hearts', 1 : 'Diamonds', 2 : 'Spades', 3 : 'Clubs'}
mapVals = {x : str(x + 2) for x in range(9)} | {9 : 'Jack', 10 : 'Queen', 11 : 'King', 12 : 'Ace'}

class Card:
	def __init__(self, suit, value):
		self.suit = suit
		self.value = value
	
	def __repr__(self):
		return f"{mapVals[self.value]} of {mapSuits[self.suit]}"

class Deck:
	def __init__(self):
		self.suits = [x for x in range(4)]
		self.vals = [x for x in range(13)]
		self.deck = [Card(x, y) for x in self.suits for y in self.vals]
	
	def __repr__(self):
		return str(self.deck)[1:-1]
	
	def shuffle(self):
		random.shuffle(self.deck)
	
	def deal(self, place, number=1):
		for _ in range(number):
			place.cards.append(self.deck.pop(0))

class Player:
	def __init__(self, name, money):
		self.name = name
		self.money = money
		self.cards = []
		self.bet = 0
		self.fold = False
	
	def __repr__(self):
		return f"Player {self.name}: £{self.money}: Bet £{self.bet}: Holding {str(self.cards)[1:-1]}"
	
	def new(self):
		self.cards = []
		self.fold = False
		self.bet = 0
	
	def placeBet(self, bet):
		self.bet += bet
		self.money -= bet

class Community:
	def __init__(self):
		self.cards = []
	
	def new(self):
		self.cards = []

class Round:
	def __init__(self, players, small, big, button):
		self.players = players
		self.playersIn = len(players)
		self.pot = 0
		self.small = small
		self.big = big
		self.button = button
		self.deck = Deck()
		self.deck.shuffle()
	
	def printPlayers(self):
		print()
		for player in self.players:
			print(player)

	def betting(self, i=None):
		if not i:
			i = (self.button + 1) % self.playersIn
			last = self.button
		else:
			self.players[(1 + self.button) % self.playersIn].placeBet(self.small)
			self.players[(2 + self.button) % self.playersIn].placeBet(self.big)
			self.currentPot = self.small + self.big
			self.bet = self.big
			last = (2 + self.button) % self.playersIn

		# main loop
		while True:
			self.printPlayers()

			# if player is only one left they've won
			if self.playersIn == 1:
				print("WOO")
				break

			# create strings for betting messages
			if not self.bet:
				options = ["Check", "Bet XX"]
				message = f"There is no current bet. You may do one of the following: {str(options)[1:-1]}"
			elif self.bet == self.players[i].bet:
				options = ["Check", "Raise XX"]
				message = f"The current bet is £{self.bet}. You may do one of the following: {str(options)[1:-1]}"
			else:
				options = ["Fold", "Call", "Raise XX"]
				message = f"The current bet is £{self.bet}. You may do one of the following: {str(options)[1:-1]}"

			curPlayer = self.players[i]
			print(f"\n{curPlayer.name}'s go")
			print(message)
			action = input("Select an option: ").lower()

			if action == "":
				break

			# fold
			if action == "fold":
				print(f"Player {curPlayer.name} has folded")
				curPlayer.fold = True
				self.playersIn -= 1
				self.players.pop(i)

				# handle loop behaviour when folding

				if i == last and self.playersIn != 1:
					break

				# if player in lower seat folds then fix this for modulo stuff 
				
				if i < last:
					last -= 1
				i %= self.playersIn
				continue

			if action == "check":
				print(f"Player {curPlayer.name} has checked")

				if i == last:
					break

				i = (i + 1) % self.playersIn
				continue

			if action == "call":
				money = self.bet - self.players[i].bet
				print(f"Player {curPlayer.name} has called")
				self.currentPot += money
				self.players[i].placeBet(money)

				if i == last:
					break

				i = (i + 1) % self.playersIn
				continue

			if "bet" in action:
				money = int(action.split(" ")[1])
				print(f"Player {curPlayer.name} has bet £{money}")
				self.bet = money
				self.currentPot += money
				self.players[i].placeBet(money)
				last = (i - 1) % self.playersIn
				i = (i + 1) % self.playersIn
				continue

			if "raise" in action:
				money = int(action.split(" ")[1])
				print(f"Player {curPlayer.name} has raised £{money}")
				self.bet = money
				money -= self.players[i].bet
				self.currentPot += money
				self.players[i].placeBet(money)
				last = (i - 1) % self.playersIn
				i = (i + 1) % self.playersIn
				continue

	def preFlop(self):
		# deal cards
		for _ in range(2):
			for i in range(self.playersIn):
				self.deck.deal(self.players[(i + self.button) % self.playersIn])
		
		# round of betting
		self.betting((self.button + 3) % self.playersIn)

class Game:
	def __init__(self, seats, small, big):
		self.seats = [None for _ in range(seats)]
		self.small = small
		self.big = big
		self.button = 0

playerList = [Player("Alice", 10000), Player("Bob", 25000), Player("Charlie", 8250), 
			  Player("David", 21000), Player("Eve", 2300)]

new = Round(playerList, 1000, 2000, 0)
new.preFlop()
new.printPlayers()
print(new.deck, len(new.deck.deck))

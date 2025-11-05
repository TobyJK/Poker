import random

class Card:
	def __init__(self, suit, value):
		self.mapSuits = {0: 'Hearts', 1: 'Diamonds', 2: 'Spades', 3: 'Clubs'}
		self.mapVals = {x: str(x + 2) for x in range(9)} | {9: 'Jack', 10: 'Queen', 11: 'King', 12: 'Ace'}

		self.suit = suit
		self.value = value
	
	def __repr__(self):
		return f"{self.mapVals[self.value]} of {self.mapSuits[self.suit]}"

class Deck:
	def __init__(self):
		self.suits = [x for x in range(4)]
		self.vals = [x for x in range(13)]
		self.cards = [Card(x, y) for x in self.suits for y in self.vals]
		self.shuffle()
	
	def __repr__(self):
		return str(self.cards)[1:-1]
	
	def shuffle(self):
		random.shuffle(self.cards)
	
	def deal(self, number=1):
		cards, self.cards = self.cards[:number], self.cards[number:]
		return cards

# player state in {0: Folded and out of hand, 1: Currently at the table bet, 2: Needs to call a bet on the table, 3: All-in and cannot make any other actions}

class Player:
	def __init__(self, name, money):
		self.name = name
		self.money = money
		self.state = 1
		self.latestPot = 0
	
	def __repr__(self):
		return f"Player {self.name}: £{self.money}"

class Pot:
	def __init__(self):
		self.lastTotal = 0
		self.bet = 0
		self.bets = {}
	
	def playerBet(self, player, bet):
		total = self.bets.get(player, 0) + bet
		self.bets[player] = total
		if total > self.bet:
			self.bet = total
	
	def newRound(self):
		self.bet = 0
		for player, bet in self.bets.items():
			self.lastTotal += bet
			self.bets[player] = 0
	
	def foldPlayer(self, player):
		if player in self.bets:
			self.lastTotal += self.bets.pop(player)
	
	def createSidePot(self, newBet):
		sidePot = Pot()
		self.bet = newBet

		for player, theirBet in self.bets.items():
			if theirBet > self.bet:
				diff = theirBet - self.bet
				sidePot.playerBet(player, diff)
				self.bets[player] -= diff
		
		return sidePot

class HoldEm:
	def __init__(self, small, big, buy, players):
		self.players = [Player(x, buy) for x in players]
		self.button = 0

game = HoldEm(1, 2, 50, ["Toby", "Lucy", "Tanheed", "Josh", "Liam", "Tom", "Harvey"])

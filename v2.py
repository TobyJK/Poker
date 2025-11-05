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

class Node:
	def __init__(self, player: Player):
		self.player = player
		self.next = None

class PlayerLinkedList:
	def __init__(self):
		self.head = None
	
	def append(self, player: Player):
		new = Node(player)
		if not self.head:
			self.head = new
			new.next = new
		else:
			this = self.head
			while this.next != self.head:
				this = this.next
			this.next = new
			new.next = self.head
	
	def traverse(self):
		this = self.head
		while True:
			print(f"{this.player} : ", end="")
			this = this.next
			if this == self.head:
				break
		print(this.player)
	
	def changeHead(self, player: Player):
		this = self.head
		while this.player.name != player:
			this = this.next
		self.head = this
	
	def delete(self, player: Player):
		if self.head.player.name == player:
			this = self.head
			while this.next != self.head:
				this = this.next
			this.next = self.head.next
			self.head = self.head.next
			return
		
		this = self.head
		while this.next.player.name != player:
			this = this.next
		this.next = this.next.next
	
	def createList(self, states=[0,1,2,3]) -> list[Player]:
		this = self.head
		l = []
		while True:
			if this.player.state in states:
				l.append(this.player)
			this = this.next
			if this == self.head:
				break
		return l

class Pot:
	def __init__(self):
		self.lastTotal = 0
		self.bet = 0
		self.bets = {}
	
	def placeBet(self, player, bet):
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
		self.players = PlayerLinkedList()
		for p in players:
			self.players.append(Player(p, buy))
		self.button = random.choice(players)
		self.players.changeHead(self.button)
		self.small = small
		self.big = big
		self.deck = Deck()
		self.pots = [Pot()]
		self.playerHands = {}
		self.community = []
	
	def handleSidePot(self, pot: Pot, bet):
		sidePot = pot.createSidePot(bet)

		if sidePot:
			self.pots.insert(self.pots.index(pot) + 1, sidePot)

			for player in self.players.createList([1, 2]):
				toCall = pot.bet - pot.bets.get(player, 0)
				if player.money > toCall:
					player.latestPot += 1

	def handleBet(self, player: Player, bet):
		pot = player.latestPot

		if bet > player.money:
			bet = player.money
			player.state = 3
		if bet == player.money:
			player.state = 3

		moneyToTake = bet
		
		# place bets in side pots if applicable
		for i in range(pot):
			toCall = self.pots[i].bet - self.pots[i].bets.get(player, 0)
			amount -= toCall
			self.pots[i].placeBet(player, toCall)
		
		# if bet is raise then make all other players go again
		if amount > self.pots[i].bet:
			self.pots[i].placeBet(player, amount)
			for p in self.pots[i].bets.keys():
				if (self.pots[i].bet - self.pots[i].bets.get(p, 0)) > 0 and p.state == 1:
					p.state = 2
		else:
			self.pots[i].placeBet(player, amount)

		# split pot if player is all-in
		allIns = [p for p in self.pots[i].bets.keys() if p.state == 3]
		if allIns:
			newBet = min([self.pots[i].bets[p] for p in allIns])
			self.handleSidePot(self.pots[i], newBet)
		
		player.money -= moneyToTake

	def newRound(self):
		fullList = self.players.createList()
		for p in fullList:
			p.latestPot = 0
			if p.money == 0:
				p.state = 0
			else:
				p.state = 2
		fullList = self.players.createList([2])

game = HoldEm(1, 2, 50, ["Toby", "Lucy", "Tanheed", "Josh", "Liam", "Tom", "Harvey"])

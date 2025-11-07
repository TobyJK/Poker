import random
from collections import Counter

class Card:
	def __init__(self, suit, value):
		self.mapSuits = {0: 'Hearts', 1: 'Diamonds', 2: 'Spades', 3: 'Clubs'}
		self.mapVals = {x: str(x + 2) for x in range(9)} | {9: 'Jack', 10: 'Queen', 11: 'King', 12: 'Ace'}

		self.suit = suit
		self.value = value
	
	def __repr__(self):
		return f"{self.mapVals[self.value]} of {self.mapSuits[self.suit]}"

	def __eq__(self, other) : 
		return self.__dict__ == other.__dict__

class Deck:
	def __init__(self):
		self.suits = [x for x in range(4)]
		self.vals = [x for x in range(13)]
		self.cards = [Card(x, y) for x in self.suits for y in self.vals]
	
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
		self.stateMapping = {0: "Folded", 1: "At table bet", 2: "Needs to call", 3: "All-in"}
	
	def __repr__(self):
		return f"Player {self.name}: £{self.money}: {self.stateMapping[self.state]}"

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
		while this.player != player:
			this = this.next
		self.head = this
	
	def delete(self, player: Player):
		if self.head.player == player:
			this = self.head
			while this.next != self.head:
				this = this.next
			this.next = self.head.next
			self.head = self.head.next
			return
		
		this = self.head
		while this.next.player != player:
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
	
	def findNext(self, player: Player) -> Player:
		this = self.head
		while this.next.player != player:
			this = this.ext
		return this.next.next.player

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
	
	def newBettingRound(self):
		self.bet = 0
		for player, bet in self.bets.items():
			self.lastTotal += bet
			self.bets[player] = 0
	
	def foldPlayer(self, player):
		if player in self.bets:
			self.lastTotal += self.bets.pop(player)
	
	def createSidePot(self, newBet):
		if newBet <= self.bet:
			return None

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
		playerList = []
		for p in players:
			new = Player(p, buy)
			self.players.append(new)
			playerList.append(new)
		self.button = random.choice(playerList)
		self.players.changeHead(self.button)
		self.button = self.players.head
		self.small = small
		self.big = big
		self.deck = Deck()
		self.possible = ["Fold", "Check", "Call", "Bet", "Raise", "Jam"]
	
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

		if bet >= player.money:
			bet = player.money
			player.state = 3
		else:
			player.state = 1

		moneyToTake = bet
		
		# place bets in side pots if applicable
		for i in range(pot):
			toCall = self.pots[i].bet - self.pots[i].bets.get(player, 0)
			bet -= toCall
			self.pots[i].placeBet(player, toCall)
		
		# if bet is raise then make all other players go again
		if bet > self.pots[pot].bet:
			self.pots[pot].placeBet(player, bet)
			for p in self.pots[pot].bets.keys():
				if (self.pots[pot].bet - self.pots[pot].bets.get(p, 0)) > 0 and p.state == 1:
					p.state = 2
		else:
			self.pots[pot].placeBet(player, bet)

		# split pot if player is all-in
		allIns = [p for p in self.pots[pot].bets.keys() if p.state == 3]
		if allIns:
			newBet = min([self.pots[pot].bets[p] for p in allIns])
			self.handleSidePot(self.pots[pot], newBet)
		
		player.money -= moneyToTake

	def currentBet(self):
		return sum([x.bet for x in self.pots])
	
	def totalBetsPlayer(self, player: Player):
		return sum([x.bets.get(player, 0) for x in self.pots])
	
	def toCall(self, player: Player):
		return self.currentBet() - self.totalBetsPlayer(player)
	
	def doAction(self, player: Player):
		print("\n")
		print(player)
		print(f"You are holding {str(self.playerHands[player])[1:-1]}. The community cards are {str(self.community)[1:-1]}")
		print(f"You have currently bet £{self.totalBetsPlayer(player)}")
		possible = self.getPossibleActions(player, self.pots[player.latestPot])
		if "Bet" in possible:
			print(f"There is no bet right now. You may do one of the following: {str(possible)[1:-1]}")
		elif "Check" in possible:
			print(f"You are at the current bet of £{self.currentBet()}. You may do one of the following: {str(possible)[1:-1]}")
		else:
			print(f"You current bet is £{self.currentBet()}. You may do one of the following: {str(possible)[1:-1]}")
		
		action = input("Select an option: ").lower()
		# self.possible = ["Fold", "Check", "Call", "Bet", "Raise", "Jam"]

		if action == "fold":
			player.state = 0
			for i in range(player.latestPot + 1):
				if player in self.pots[i].bets:
					self.pots[i].foldPlayer(player)
			return False
		
		if action == "check":
			player.state = 1
			return False
		
		if action == "call":
			self.handleBet(player, self.toCall(player))
			return False
		
		if "bet" in action:
			amount = int(action.split(" ")[1])
			self.handleBet(player, amount)
			return True
		
		if "raise" in action:
			amount = int(action.split(" ")[1])
			self.handleBet(player, amount - self.totalBetsPlayer(player))
			return True
		
		if action == "jam":
			if player.money > self.toCall(player):
				self.handleBet(player, self.totalBetsPlayer(player) + player.money)
				return True
			self.handleBet(player, self.toCall(player))
			return False
		
		raise SyntaxError("Please enter a valid instruction.")

	def betting(self):
		# create order for betting to 1 more than current head
		self.players.changeHead(self.players.head.next.player)
		order = self.players.createList([1,2])
		while order:
			playerToAct = order.pop(0)
			if self.doAction(playerToAct):
				self.players.changeHead(playerToAct)
				self.players.head = self.players.head.next
				order = self.players.createList([2])
			else:
				pass
		
		# collect all bets into pots
		for pot in self.pots:
			pot.newBettingRound()

	def getPossibleActions(self, player: Player, pot: Pot):
		# self.possible = ["Fold", "Check", "Call", "Bet", "Raise", "Jam"]
		if player.state == 1:
			possible = [x for x in self.possible if x not in ["Fold", "Call", "Raise", "Bet"]]
			if pot.bet:
				possible.append("Raise")
			else:
				possible.append("Bet")
		elif player.state == 2:
			possible = [x for x in self.possible if x not in ["Check", "Bet"]]
		else:
			possible = []
		return possible
	
	def checkIfOver(self):
		if len(self.players.createList([1])) <= 1:
			return True
		return False
	
	def flushCheck(self, cards: list[Card]) -> list[Card]:
		commonSuit = Counter([x.suit for x in cards]).most_common(1)[0]
		if commonSuit[1] < 5:
			return []
		cardsInSuit = sorted([x for x in cards if x.suit == commonSuit[0]], key=lambda x: x.value, reverse=True)
		return cardsInSuit

	def straightCheck(self, cards: list[Card]) -> list[Card]:
		cards.sort(key=lambda x: x.value, reverse=True)
		for i in range(len(cards) - 4):
			straight = [cards[i]]
			for j in range(i, len(cards) - 1):
				if cards[j].value - cards[j + 1].value == 1:
					straight.append(cards[j + 1])
				else:
					break
			if len(straight) >= 5:
				return straight
		return []

	def straightFlushCheck(self, cards: list[Card]) -> list[Card]:
		cards = self.flushCheck(cards)
		if not cards:
			return []
		
		return self.straightCheck(cards)[:5]

	def royalFlushCheck(self, cards: list[Card]) -> list[Card]:
		cards = self.straightFlushCheck(cards)
		if not cards:
			return []
		if cards[0].value == 12:
			return cards
		return []

	def multiplesCheck(self, cards: list[Card]) -> list[int, list[Card]]:
		cards.sort(key=lambda x: x.value, reverse=True)
		cardCounts = Counter([x.value for x in cards])
		mostCommon = cardCounts.most_common(1)[0]

		if mostCommon[1] == 4:
			return [6, [x for x in cards if x.value == mostCommon[0]] + [[x for x in cards if x.value != mostCommon[0]][0]]]
		
		fullTwo = cardCounts.most_common(2)
		if fullTwo[0][1] == 3 and fullTwo[1][1] >= 2:
			return [5, [x for x in cards if x.value == mostCommon[0]] + [x for x in cards if x.value == fullTwo[1][0]][:2]]
		
		if mostCommon[1] == 3:
			return [2, [x for x in cards if x.value == mostCommon[0]] + [x for x in cards if x.value != mostCommon[0]][:2]]
		
		if fullTwo[0][1] == fullTwo[1][1] == 2:
			return [1, [x for x in cards if x.value in [fullTwo[0][0], fullTwo[1][0]]] + [[x for x in cards if x.value != mostCommon[0]][0]]]
		
		if mostCommon[1] == 2:
			return [0, [x for x in cards if x.value == mostCommon[0]] + [x for x in cards if x.value != mostCommon[0]][:3]]
		
		return [-1, cards[:5]]

	def bestHandKickers(self, num, hands: dict[Player: list[Card]]) -> list[Player]:
		players = [x for x in hands]
		i = 0
		while i < num:
			highestCard = -1
			best = []
			for player in players:
				firstCard = hands[player][i].value
				if firstCard > highestCard:
					highestCard = firstCard
					best = [player]
				elif firstCard == highestCard:
					best.append(player)
			if len(best) == 1:
				return best
			i += 1
			players = [x for x in best]
		return best

	def findWinners(self, players: list[Player]) -> list[Player]:
		playerHands = {x: self.playerHands[x] for x in players}
		playerScores = {x: None for x in players}
		playerBestHands = {x: None for x in players}

		for player in players:
			cards = playerHands[player] + self.community

			x = self.royalFlushCheck(cards)
			if x:
				playerScores[player] = 8
				playerBestHands[player] = x
				continue

			x = self.straightFlushCheck(cards)
			if x:
				playerScores[player] = 7
				playerBestHands[player] = x
				continue

			ans = self.multiplesCheck(cards)
			if ans[0] == 6:
				playerScores[player] = 6
				playerBestHands[player] = ans[1]
				continue
			
			if ans[0] == 5:
				playerScores[player] = 5
				playerBestHands[player] = ans[1]
				continue

			x = self.flushCheck(cards)
			if x:
				playerScores[player] = 4
				playerBestHands[player] = x[:5]
				continue

			x = self.straightCheck(cards)
			if x:
				playerScores[player] = 3
				playerBestHands[player] = x[:5]
				continue

			if ans[0] == 2:
				playerScores[player] = 2
				playerBestHands[player] = ans[1]
				continue
			
			if ans[0] == 1:
				playerScores[player] = 1
				playerBestHands[player] = ans[1]
				continue

			if ans[0] == 0:
				playerScores[player] = 0
				playerBestHands[player] = ans[1]
				continue
			
			playerScores[player] = -1
			playerBestHands[player] = ans[1]

		bestHand = max(playerScores.values())
		players = [x for x in players if playerScores[x] == bestHand]
		if len(players) == 1 or bestHand == 8:
			return players
		
		return self.bestHandKickers(5, {x: playerBestHands[x] for x in players})

	def end(self):
		self.players.head = self.button

		for pot in self.pots:
			playersIn = list(pot.bets.keys())
			if len(playersIn) == 1:
				total = pot.lastTotal + sum(pot.bets.values())
				playersIn[0].money += total
				print(f"{playersIn[0].name} wins £{total}")
				continue

			if len(self.community) != 5:
				self.community += self.deck.deal(5 - len(self.community))
				print(f"Community cards are now {str(self.community)[1:-1]}")
			
			winners = self.findWinners(playersIn)
			print(winners)
			win = (pot.lastTotal + sum(pot.bets.values())) // len(winners)
			for player in winners:
				player.money += win
			
			left = (pot.lastTotal + sum(pot.bets.values())) - (win * len(winners))
			if left:
				playerOrder = self.players.createList()
				for player in playerOrder:
					if player in winners:
						player.money += left
						break

	def newRound(self):
		fullList = self.players.createList()
		print(fullList)
		for p in fullList:
			p.latestPot = 0
			if p.money == 0:
				p.state = 0
			else:
				p.state = 2
		fullList = self.players.createList([2])

		self.pots = [Pot()]
		self.deck.shuffle()

		# post blinds
		offset = 0
		if len(fullList) == 2:
			offset = 1
		small = fullList[1 - offset]
		big = fullList[2 - offset]
		self.handleBet(small, self.small)
		self.handleBet(big, self.big)
		print(f"Dealer: {self.button.player}, SB: {small}, BB: {big}")

		# deal cards
		self.playerHands = {x: [] for x in fullList}
		self.community = []

		self.players.changeHead(fullList[1])
		dealList = self.players.createList([1, 2])
		for _ in range(2):
			for p in dealList:
				self.playerHands[p] += self.deck.deal()
		
		# set up action for preflop
		self.players.changeHead(big)
		self.betting()
		print(self.players.createList())
		print(self.playerHands)

		if self.checkIfOver():
			self.end()

if __name__ == "__main__":
	game = HoldEm(1, 2, 50, ["Toby", "Lucy", "Tanheed", "Josh", "Liam", "Tom", "Harvey"])
	game.newRound()

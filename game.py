
from card import Card
from computer import Computer
from kripke_model import KripkeModel
import random

class Game:
	def __init__(self, players):
		self.cards = set()
		self.deck = []
		self.attacking_cards = []
		self.defending_cards = []
		self.discard_pile = []
		self.outcome = 0
		
		# smallest card that every player could not defend
		self.smallest = [[8] * 4 for y in range(len(players))]

		self.players = players
		self.kripke_model = {} # {<card>: KripkeModel(states={<player>: <world_number>}, relations={<player>: set((<world_number>, <world_number>))})}
		self.common_knowledge = {}
		self.attacker = players[0]
		self.defender = players[1]
	
	def start(self):
		""" Initialize the deck and deal the starting hands. """
		trump_value = random.choice(list(Card.values))
		trump_suit = random.choice(Card.suits)
		self.trump_card = Card(trump_value, trump_suit, True)
		
		for value in Card.values:
			for suit in Card.suits:
				if suit == trump_suit and suit == trump_value: # skip trump card, we will add it later
					continue
				is_trump = (suit == trump_suit)
				card = Card(value, suit, is_trump)
				self.cards.add(card)
				self.deck.append(card)
		
		# shuffle the deck
		random.shuffle(self.deck)
		
		# add the trump card to the bottom of the deck
		self.deck.insert(0, self.trump_card)
		
		# deal cards
		for index, player in enumerate(self.players):
			player.joinGame(self)
			for i in range(6):
				card = self.deck.pop() # take the top card from the deck
				player.takeCard(card) # add it to the players hand
		
		# create kripke model for each card
		for card in self.cards:
			states = {player: index for player, index in enumerate(self.players)}
			relations = {
				player: set((i, j) for i in range(len(self.players)) for j in range(len(self.players)))
				for player in self.players
			}
			self.kripke_model[card] = KripkeModel(states, relations)
		
		# the trump card is not in any of the player's hands and they all know it
		self.kripke_model[self.trump_card].states = {}
		for player in self.players:
			self.kripke_model[self.trump_card].relations[player] = {}
	
	def stop(self):
		""" Resets the game. """
		self.cards = set()
		self.deck = []
		self.attacking_cards = []
		self.defending_cards = []
		self.discard_pile = []
		self.kripke_model = {}
		
		for player in self.players:
			player.hand = []

	def next_player(self, player):
		""" Return next player that has cards """
		for i in range(len(self.players)):
			if player == self.players[i]:

				if len(self.players[(i+1) % 4].hand) > 0:
					return self.players[(i+1) % 4]

				elif len(self.players[(i+2) % 4].hand) > 0:
					return self.players[(i+2) % 4]

				else:
					return self.players[(i+3) % 4]


	def next_turn(self, outcome):

		# player defended succesfully, so
		# defender becomes new attacker
		if outcome == 0:
			self.attacker = self.defender

			self.defender = self.next_player(self.attacker)

		# player failed to defend, so
		# defender skips turn to attack
		else:
			self.attacker = self.next_player(self.defender)

			self.defender = self.next_player(self.attacker)

	def new_attack(self):

		out = False

		while not out:
			
			attacking_card = self.attacker.playCard(self.attacker, self.defender)
			
			print('attacking card chosen ...')
			if attacking_card is None:
				return 0

			self.attacker.hand.remove(attacking_card)
			for player in self.players:
				if player != self.attacker:
					self.kripke_model[attacking_card].removePossibleWorld(player)

			
			defending_card = self.defender.playCard(self.attacker, self.defender, attacking_card)
			print('defending card chosen ...')
			if defending_card is None:
				out = True
			else:
				self.defender.hand.remove(defending_card)
				for player in self.players:
					if player != self.defender:
						self.kripke_model[defending_card].removePossibleWorld(player)
		return 1

	def has_ended(self):

		counter = 0

		for player in self.players:
			if len(player.hand) > 0 :
				counter += 1

		if counter > 1:
			return False
		else:
			return True

def main():
	player_count = 4

	
	# create players
	players = []
	for i in range(player_count):
		player = Computer()
		players.append(player)
	
	# create a new game and let the players take actions until the game has ended
	game = Game(players)
	game.start()

	while not game.has_ended():

		print('New attack ...')
		outcome = game.new_attack()

		print('End of turn')
		game.next_turn(outcome)

if __name__ == '__main__':
	main()

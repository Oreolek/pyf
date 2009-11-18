import states, lib

import props, utils
from items import Item
from errors import *

class Actor(Item):
	'''Class for player characters. Handles sentences for examining the surroundings, 
	moving, saving and loading the game.'''
	name = 'yourself', 'player', 'self'
	definite = 'yourself'
	indefinite = 'yourself'
	pronoun = None
	
	WAIT = 'wait'
	INVENTORY = 'inventory'
	NOT_A_DIRECTION = "notADirection"
	'''Printed when player tries to move into a non-direction.'''
	NO_DIRECTION = "noDirection"
	"""Printed when player attempts to just walk."""
	CANT_DO = "cantDo"
	"""Printed when player can't use verb %s on noun %s."""
	TOUCH = 'touch'
	"""Printed when player feels a generic object."""
	INVENTORY = 'inventory'
	"""Printed when player requests to display the inventory."""
	NO_VIOLENCE = 'noViolence'
	"""Printed as a response to attacks against random nouns."""
	UNHANDLED = "unhandled"
	"""Printed as a final error message when every check fails."""
	SOCIAL_UNHANDLED = "socialUnhandled"
	"""Printed when player attempts a social action."""
	SOCIAL_TOUCH_UNHANDLED = "socialUnhandled"
	"""Printed when player attempts a social touching action."""
	LISTEN = "listen"
	"""Default response for "listen"."""
	PUSH = "push"
	"""Printed when player attempts to push things without a direction."""
	NOT_NEAR = "notNear"
	'''Printed when player needs to approach object before interacting with it.'''
	ITEM_UNAVAILABLE = "itemUnavailable"
	'''Shown when the parser recognizes noun, but it's unavailable to actor.'''
	VERB_UNKNOWN = "verbUnknown"
	
	NOT_EDIBLE = 'notEdible'
	
	SCORE = 'score'
	'''Display score'''
	
	ZERO_LENGTH_SENTENCE = "zeroLengthSentence"
	"""Printed when player's input is an emptry string."""
	
	responses = {
		NOT_A_DIRECTION : "[sentence[1].name] is not a direction.",
		NO_DIRECTION : "You should specify which direction you want to walk to.",
		TOUCH : "You feel nothing unexpected.",
		CANT_DO : "You can't [verbs[0].name] [self.definite].",
		ZERO_LENGTH_SENTENCE : "I don't understand what you mean.",
		ITEM_UNAVAILABLE : "You can't see anything like that here.",
		'verbKnown' : "I only understood that you want to [verbs[0].name] something.",
		UNHANDLED : "I don't know what that means.",
		NO_VIOLENCE : "Violence never solves anything.",
		INVENTORY : "You're carrying %s.",
		SOCIAL_UNHANDLED : "[self.definite] doesn't seem to notice.",
		SOCIAL_TOUCH_UNHANDLED : "You doubt [self.pronoun] would like that very much.",
		LISTEN : "You hear nothing unexpected.",
		WAIT : 'Time passes.',
		PUSH : "You'd have to specify where you want to push [self.definite].",
		'saved' : "Saved!",
		'loaded' : "Loaded!",
		SCORE : "You've earned %i points so far.",
		NOT_NEAR : '(first walking %s)',
		VERB_UNKNOWN : "You can't [sentence.words[0].name] things.",
		NOT_EDIBLE : "[nouns[0].definite] [nouns[0].verbPlural and 'are' or 'is'] hardly edible.",
	}

	LOOK = "look"
	'''Verb used to get a description of the player's surroundings.'''
	
	def __init__(self):
		Item.__init__(self)
		self.pronouns = {}
		
		self.state = states.Running(self)
		'''State to handle any input for this actor.'''
		
		self.output = None
		'''Output object last associated with this actor.'''

	def input(self, sentence, output):
		self.output = output
		self.lastInput = sentence
		output.actor = self
		output.sentence = sentence
		sentence.actor = self

		'''TODO:	Implement a recursive function to account for multiple
					ambiguous words in one sentence.'''
		try:
			self.ownerGame.lib.parse(sentence)
		except AmbiguityError, e:
			state = states.Disambiguation(self, e)
			self.state = state

			if state.tryResolve():
				output.write("(%s)" % state.words[0].word.name, False)
				state.resumeMatching(state.words[0])
				sentence = state.sentence
			else:
				output.write(self.state.message(), False)
				return output

		if len(sentence) == 0:
			try:
				self.unhandledSentence(sentence, output)
			except OutputClosed:
				pass
			return output
		self.ownerGame.turns += 1

		for word in sentence:
			if issubclass(word.__class__, lib.Noun):
				if word.item.pronoun != None:
					try:
						if word.item.pronoun in self.pronouns:
							self.pronouns[word.item.pronoun].removeWord(word.item.pronoun)
					except ValueError:
						pass

					word.addWord(word.item.pronoun)
					self.pronouns[word.item.pronoun] = word

		self.state.handle(sentence, output)


	
	def unhandledSentence(self, sentence, output):
		if len(sentence) == 0:
			self.write(output, self.ZERO_LENGTH_SENTENCE)
			
		if sentence[0] == '*verb':

			if len(sentence) == 1:
				if sentence == 'go':
					self.write(output, self.NO_DIRECTION)
				elif sentence == 'z':
					self.write(output, self.WAIT)
				elif sentence == 'listen':
					self.write(output, self.LISTEN)

			if len(sentence) == 2:
				if sentence[0] == 'go':
					output.write(self.responses[self.NOT_A_DIRECTION])
			
				elif sentence[1] == '*noun':
					item = sentence[1].item
					if self.canAccess(item):
						if sentence[0] == 'push':
							output.write(self.responses[self.PUSH])
						elif sentence[0] == "*social":
							output.write(self.responses[self.SOCIAL_UNHANDLED])
						elif sentence[0] == "*socialtouch":
							output.write(self.responses[self.SOCIAL_TOUCH_UNHANDLED])
						elif sentence[0] == 'touch':
							output.write(self.responses[self.TOUCH])
						elif sentence[0] == '*attack':
							self.write(output, self.NO_VIOLENCE)
						elif sentence[0] == 'eat':
							self.write(output, self.NOT_EDIBLE)
						output.write(self.responses[self.CANT_DO])
					else:
						self.write(output, self.ITEM_UNAVAILABLE)
				else:
					output.write(self.responses['verbKnown'])
		
		self.write(output, 'unhandled')
		
	def handle(self, sentence, output):
		if sentence == 'inventory':
			self.inv(output)
			
	@property
	def state(self):
		return self._state
		
	@state.setter
	def state(self, value):
		self._state = value
		
	def handlePrivate(self, sentence, output):
		Item.handlePrivate(self,sentence,output)
		self.handleMove(sentence, output)
		
		if sentence == self.LOOK:
			self.lookAround(output)
		elif sentence == 'save':
			self.game.pickle()
			self.write(output, 'saved')
		elif sentence == "restore":
			self.game.unpickle()
			self.write(output, 'loaded')
		elif sentence == 'score':
			self.score(output)
			
	def score(self, output):
		output.write(self.responses[self.SCORE] % self.ownerGame.score)
			
	def handleMove(self, sentence, output):
		'''Called to handle movement requests.
		
		sentence : Sentence
		output : Output'''
		try:
			d = self.getMoveDir(sentence)
		except ValueError:
			return

		room = self.owner.tryAccess(d, output)
		self.move(room)
		self.newLocation(output)
		
	def inv(self, output):
		'''Write object inventory on output.

		output : output'''
		l = []
		for item in self.inventory:
			if props.Mobile in item.props:
				l.append(item.Normal.getDesc('inv'))
				
		if len(l) == 0:
			l.append('nothing')
		output.write(self.responses[self.INVENTORY] % utils.naturalJoin(l, ', ', ' and '))

		output.close()

	
		
	def lookAround(self, output, short=False):
		'''Write the current room description.
		
		output : Output
		short : bool - Whether to write the short description of the room.'''
		output.write('<h4>' + self.owner.name + '</h4>', False)

		if short:
			output.close()
		else:
			output.write(self.owner.Normal.getLong())
		
	def newLocation(self, output):
		'''Called to write description of a new location. If room has been visited before
		will write the short description.
		
		output : Output'''
		if self.owner.visited:
			self.lookAround(output, True)
		else:	
			self.owner.visited = True
			self.lookAround(output, False)

			
	def getMoveDir(self, sentence):
		'''Get movement direction from sentence.
		
		sentence : Sentence'''
		if sentence == 'go *direction':
			return sentence[1]
		elif sentence == '*direction':
			return sentence[0]
			
		raise ValueError('Sentence "%s" has no movement direction.' % str(sentence))
'''Basic classes for defining the game world.'''

"""This file is part of PyF.

PyF is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyF is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyF.  If not, see <http://www.gnu.org/licenses/>."""

import lib, states, script, items, output
from handler import Handler
from errors import *

class Game(Handler):
	inst = None
	lib = lib.standardLib()
	inventory = []
	actor = None
	
	name = "Untitled Game"
	version = "0.1"
	author = "Pai Ef"
	IFID = ''
	
	savefile = 'default.save'
	
	description = ""
	intro = ""
	
	debug = True
	
	EVT_PICKLE = 'gameSave'
	EVT_UNPICKLE = 'gameLoad'
	
	l = []
	
	script = None
	
	responses = {
		'zeroLengthSentence' : "I don't understand."
	}
	
	def __init__(self):
		self.__class__.l.append(self)
		self.__class__.inst = self
		Handler.__init__(self)
		self.lib = self.lib
		self.turns = 0
		self.state = None
		self.setState(states.Running(self))
		self.pronouns = {}
		self.output = None
		self.timedEvents = []
		
		if self.script != None:
			s = self.script.read()
			self.script.close()
			self.script = s
			
	def ownerGame(self):
		return self
		
	def debugger(self):
		'''Run the Python command line debugger.'''
		import pdb
		print "Initiating Python debugger"
		print "--------------------------"
		print 'Type "dir()" to see all the variables in current scope.' 
		print 
		pdb.set_trace()
		
		
	def setState(self, state):
		self.state = state
		
	def end(self, output):
		'''End the game setting the state as finished and writing final output.'''
		self.setState(states.Finished(self))
		self.ending(output)
		
	def ending(self, output):
		'''Write final output before the end of the game.'''
		output.write("You have won.")
		
	def cleanInput(self, s):
		'''Clean input of unwanted characters.
		
		s : str
		
		returns : str'''
		s = s.replace('*', '')
		return s
	
	def input(self, s):
		'''Handle user input and return output.
		
		s : string
		
		returns : Output'''
		s = self.cleanInput(s)
		o = output.Output()

		if s == 'pdb' and self.debug:
			self.debugger()
			o.write('Debugger closed', False)
			return o
			
		try:
			s = self.lib.parse(s)
		except AmbiguityError, e:
			state = states.Disambiguation(self, e)
			self.setState(state)
			
			if state.tryResolve():
				state.resumeMatching(state.words[0])
				s = state.sentence
			else:
				o.write(self.state.message(), False)
				return o
				
		self.actor.input(s, o)
			
		if len(s) == 0:
			try:
				self.unhandledSentence(s, o)
			except OutputClosed:
				pass
			return o
		self.output = o
		self.turns += 1
		
		
		for word in s:
			if issubclass(word.__class__, lib.Noun):
				o.target = word.item
				if word.item.pronoun != None:
					try:
						if word.item.pronoun in self.pronouns:
							self.pronouns[word.item.pronoun].removeWord(word.item.pronoun)
					except ValueError:
						pass

					word.addWord(word.item.pronoun)
					self.pronouns[word.item.pronoun] = word
						
		self.state.handle(s, o)
		o.open()
		
		o.canClose = False
		l = self.timedEvents
		self.timedEvents = []
		for event in l:
			if event(s, o):
				self.timedEvents.append(event)
		o.canClose = True
		
		self.output = None
		return o
		
	def delPronouns(self):
		'''Clear the pronoun list.'''
		for word in self.pronouns:
			self.pronouns[word].removeWord(word)
		
	def writeIntro(self, output):
		'''Write game intro.
		
		output : Output'''
		output.write(self.description, False)
		output.write('<b>' + self.name + '</b>', False)
		#output.write('by <b>' + self.author + '</b>', False)
		#output.write('Version ' + self.version, False)
		output.write(self.intro, False)
		
		self.actor.newLocation(output)

		output.close()
	
	def getIntro(self):
		'''Create new output object and write game intro on it.
		
		returns : Output'''
		o = output.Output()
		try:
			self.writeIntro(o)
		except OutputClosed:
			pass
		return o

	def handle(self, sentence, output):
		if sentence == 'inventory':
			output.write("You're currently carrying: ", False)
			self.inv(output)
		else:
			self.unhandledSentence(sentence, output)
			
	def unhandledSentence(self, sentence, output):
		if len(sentence) == 0:
			self.write(output, 'zeroLengthSentence')
		else:
			self.actor.unhandledSentence(sentence, output)
		
	def setActor(self, o):
		'''Set game actor.
		
		o : Actor'''
		self.actor = o
		
	def inv(self, output):
		'''Write object inventory on output.
		
		output : output'''
		for item in self.actor.inventory:
			output.write(item.Normal.getDesc('inv'), False, obj=item)
		
		output.close()
		
	def addItem(self, item):
		'''Instantiate ItemClass and add it to the game world.
		
		item : Item subclass'''
		self.inventory.append(item)
		self.lib.append(item.word)
		item.updateAccessInfo(self)
		
	def addItems(self, *items):
		'''Add items to the game world.
		
		*items : Item'''
		for item in items:
			self.addItem(item)
			
	def initFromScript(self, dict):
		'''Init this game from current script.
		
		dict - Dict mapping node names to classes.'''
		self.script = script.XMLScript(self.script, dict)
		
		for child in self.script.createChildren(None):
			if issubclass(type(child), items.Item):
				self.addItem(child)
			
	def pickle(self):
		'''Pickle the current game state and write it into self.savefile. You can
		override this behaviour by adding EVT_PICKLE listener to this game object and
		raising OutputClosed.'''
		self.dispatchEvent(GameEvent(self.EVT_PICKLE))
		import cPickle as pickle
		
		f = open(self.savefile, 'w')
		s = pickle.dumps(self)
		f.write(s)
		f.close()
		
	def __getstate__(self):
		return (self.inventory, self.lib, self.actor, self.state, self.pronouns, self.turns)
		
	def unpickle(self):
		'''Unpickle self.savefile and load it as current game state. You can
		override this behaviour by adding EVT_UNPICKLE listener to this game object and
		raising OutputClosed.'''
		self.dispatchEvent(GameEvent(self.EVT_UNPICKLE))
		import cPickle as pickle
		
		f = open(self.savefile, 'r')
		self.__setstate__(pickle.loads(f.read()).__getstate__())
		f.close()
		
	def __setstate__(self, f):
		self.inventory = f[0]
		for item in self.inventory:
			item.updateAccessInfo(self)
		self.lib = f[1]
		self.actor = f[2]
		self.state = f[3]
		self.state.game =	self
		self.pronouns = f[4]
		self.turns = f[5]
		
class GameEvent:
	def __init__(self, type):
		self.type = type
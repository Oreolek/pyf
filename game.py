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
from handler import Handler, HandlerEvent
from errors import *

class Game(Handler):
	'''Superclass for any PyF games.'''
	
	lib = lib.standardLib()
	'''Lib to use for parsing user input.'''
	inventory = []
	'''List of all items currently in the game.'''

	name = "Untitled Game"
	'''The title of the game.'''
	version = "0"
	'''Version of the game.'''
	author = "Pai Ef"
	'''Author name.'''
	IFID = ''
	
	savefile = 'default.save'
	'''Default file to use for saving and loading game.'''
	
	description = ""
	'''Description of the game; invoked in intro the title is shown.'''
	intro = ""
	'''Description of the game; invoked in intro after the title.'''
	
	debug = True
	'''Allow invoking pdb.'''
	transcribe = False
	'''True if the game should automatically enable transcription.'''
	
	EVT_PICKLE = 'gameSave'
	'''Fired when user writes tries to save through the text interface.'''
	EVT_UNPICKLE = 'gameLoad'
	'''Fired when user writes tries to load through the text interface.'''
	
	script = None
	'''File-like object to instantiate into XMLScript.'''
	
	def __init__(self):
		'''Init game.'''
		Handler.__init__(self)
		self.turns = 0
		'''Holds the number of turns that have passed. Ticks up every time 
		Game.input is called.'''
		self.actor = None
		'''Default actor to pass input to.'''
		
		if self.script != None:
			s = self.script.read()
			self.script.close()
			self.script = s
			
		self.scoreList = {}
	
	@property
	def ownerGame(self):
		return self
		
	def addScore(self, amount, id):
		'''Used to add to the game score counter.
		
		@type	amount:	int
		@type	id:	str
		@param	id:	A unique ID describing what the points have been awarded for. 
					Should be human readable, eg. "eating blueberry pie".'''
		if id not in self.scoreList:
			self.scoreList[id] = amount
			
	@property
	def score(self):
		i = 0
		for score in self.scoreList.keys():
			i += score
		return i
		
	def debugger(self):
		'''Inspect game state through Python command line debugger.'''
		import pdb
		print "Initiating Python debugger"
		print "--------------------------"
		print 'Type "dir()" to see all the variables in current scope.' 
		print 
		pdb.set_trace()
		
		
	def setState(self, state):
		'''DEPRECATED. Use 
			Game.actor.state = State
		instead.'''
		self.actor.state = state
		
	def end(self, output):
		'''End the game setting the state as finished and writing final output.'''
		self.actor.state = states.Finished(self.actor)
		self.ending(output)
		
	def ending(self, output):
		'''Write final output before the end of the game.'''
		output.write("You have won.")
		
	def cleanInput(self, s):
		'''Clean input of unwanted characters.
		
		@type	s:	str
		
		@rtype	:	str'''
		s = s.replace('*', '')
		return s
		
	def getItem(self, name):
		'''Get item with name. Raise KeyError if not in game.
		
		@type	name:	str
		@rtype	:		Item'''
		for item in self.inventory:
			if item.name == name:
				return item
		raise KeyError("Game inventory has no item %s" % name)
	
	def input(self, s):
		'''Handle user input and return output.
		
		@type	s:	str
		
		@rtype	:	Output'''
		s = self.cleanInput(s)
		o = output.Output()

		if s == 'pdb' and self.debug:
			self.debugger()
			o.write('Debugger closed', False)
			return o
			
		s = lib.Sentence(s.encode())
		self.actor.input(s, o)
		
		if self.transcribe:
			if not hasattr(self, 'transcription'):
				import datetime
				self.transcription = open("%s-%s.txt" % (self.name, datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M")), 'w')
			self.transcription.write(self.actor.state.request + ' ' + s.s + '\n')
			self.transcription.write('\n'.join(o.lines) + '\n')

		return o
		
	def writeIntro(self, output):
		'''Write game intro.
		
		@type	output:	Output'''
		output.write(self.description, False)
		output.write('<h1>' + self.name + '</h1>', False)
		#output.write('by <b>' + self.author + '</b>', False)
		#output.write('Version ' + self.version, False)
		output.write(self.intro, False)
		
		self.actor.newLocation(output)

		output.close()
	
	def getIntro(self):
		'''Create new output object and write game intro on it.
		
		@rtype:	Output'''
		o = output.Output()
		try:
			self.writeIntro(o)
		except OutputClosed:
			pass
		return o

	def handle(self, sentence, output):
		pass
			
	@property
	def actor(self):
		return self._actor
		
	@actor.setter
	def actor(self, value):
		self._actor = value
		
	def setActor(self, o):
		'''DEPRECATED. Use 
			Game.actor = Actor
		instead.'''
		self.actor = o
		
	def addItem(self, item):
		'''Instantiate ItemClass and add it to the game world.
		
		item : Item subclass'''
		self.inventory.append(item)
		self.lib.append(item.word)
		item.updateAccessInfo(self)
		item.init()
		
	def addItems(self, *items):
		'''Add items to the game world.
		
		*items : Item'''
		for item in items:
			self.addItem(item)
			
	def removeItem(self, item):
		'''Remove item and its word from game.
		
		@type	item:	Item
		@param	item:	item to remove.'''
		
		if item.owner != None:
			item.owner.inventory.remove(item)
		item.owner = None
		
		item.removeWord()
		self.inventory.remove(item)
		item.game = None
			
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
		return (self.inventory, self.lib, self.actor, self.turns, self.scoreList)
		
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
		self.turns = f[3]
		self.scoreList = f[4]
		
class GameEvent(HandlerEvent):
	def __init__(self, type):
		HandlerEvent.__init__(self, type, None)
		self.type = type
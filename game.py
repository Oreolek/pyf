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
	
	script = None
	
	def __init__(self):
		self.__class__.inst = self
		Handler.__init__(self)
		self.lib = self.lib
		self.turns = 0
		self.output = None
		
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
		@param	id:	A unique ID describing what the points have been
					awarded for. Should be human readable, eg. 
					"eating blueberry pie".'''
		if id not in self.scoreList:
			self.scoreList[id] = amount
			
	@property
	def score(self):
		i = 0
		for score in self.scoreList.keys():
			i += score
		return i
		
	def debugger(self):
		'''Run the Python command line debugger.'''
		import pdb
		print "Initiating Python debugger"
		print "--------------------------"
		print 'Type "dir()" to see all the variables in current scope.' 
		print 
		pdb.set_trace()
		
		
	def setState(self, state):
		self.actor.state = state
		
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
		
	def getItem(self, name):
		for item in self.inventory:
			if item.name == name:
				return item
		raise KeyError("Game inventory has no item %s" % name)
	
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
			
		s = lib.Sentence(s.encode())
		self.actor.input(s, o)
		
		self.output = None
		return o
		
	def writeIntro(self, output):
		'''Write game intro.
		
		output : Output'''
		output.write(self.description, False)
		output.write('<h1>' + self.name + '</h1>', False)
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
		pass
			
	def setActor(self, o):
		'''Set game actor.
		
		o : Actor'''
		self.actor = o
		
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
			
	def removeItem(self, item):
		'''Remove item and its word from game.
		
		@type	item:	Item
		@param	item:	item to remove.'''
		
		try:
			item.owner.inventory.remove(item)
		except AttributeError:
			pass
			
		item.owner = None
		self.inventory.remove(item)
		self.lib.remove(item.word)
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
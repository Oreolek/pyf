"""Basic game world item classes."""

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
along with PyF.  If not, see <http://www.gnu.org/licenses/>.
"""

import utils, inventory, new, handler, props

from handler import Handler
from errors import *

import lib, copy

class Item(Handler):
	'''Item is the base class for all the items in PyF game world.'''
	
	EVT_MOVED = 'itemMoved'
	'''Called before the item is moved around in the game world.'''
	EVT_INT_MOVED = 'itemIntMoved'
	'''Called before the item is moved internally in its owner.'''
	EVT_ITEM_RECEIVED = "itemReceived"
	'''Called before an item dest is added to item's inventory.'''
	EVT_ITEM_HANDLE = "itemHandle"
	EVT_OWNED_ITEM_HANDLE = "itemOwnedItemHandle"
	
	EVT_INIT = "itemInit"
	i = None
	inits = {}
	
	name = None
	'''tuple - The first item is converted into instance name. The rest
	are turned into synonyms of name for the game library.'''
	
	location = None
	'''Stores item's physical location in its owner.'''
	
	pronoun = 'it'
	'''str - Allows the parser to refer to the object as its pronoun after
	handling it.'''
	
	proxy = False
	'''Proxy classes are blocked from inventory listings.'''
	
	inst = None
	
	# default values
	adjective = ()
	'''tuple - Strings in tuple are converted into adjectives for the Word
	name. Adjectives can be used to match words more accurately.'''
	props = ()
	'''tuple - props to attach to the Item during instance 
	construction. Property instances are deepcopied during construction.'''
	accessible = True
	'''bool - Controls whether the item is accessible in the game world. This
	can be used to hide the object regardless of its real location in the game world.
	May be manipulated by props.'''
	owner = None
	'''Item instance - Owner of this item in the game world.'''
	definite = None
	'''str - Definite name of this item, eg. "the book".'''
	indefinite = None
	'''str - Indefinite name of this item, eg. "a book".'''
	
	spaceAware = False
	'''True if the player needs to share the owner of this item to touch it.'''
	
	wordClass = lib.Noun
	'''The Word class in which the name is instantiated.'''
	
	listeners = {}
	
	responses = {
		'notNear' : '(first walking %s)'
	}
	
	def __init__(self):
		Handler.__init__(self)

		cls = self.__class__
		cls.inst = self
		
		if cls.name != None:
			self.initWord(cls.name)
		
		self.props = ()
		self.inventory = inventory.Inventory(self)
		#: list - contains all the items this item owns
		
		self.newprops = []
		self.accessible = cls.accessible
		
		if cls.owner != None:
			self.owner = None
			self.move(cls.owner)
		else:
			self.owner = None
			
		if cls.location != None:
			self.intMove(cls.location)

		props = cls.props
		if props.__class__ != tuple:
			props = (props,)

		for prop in props:
			prop = prop.clone()
			self.addProp(prop)
			
		self.finalizeProps()
		self.dispatchEvent(self.EVT_INIT)
		
	def __eq__(self, other):
		if type(self) == other:
			return True
		else:
			id(self) == id(other)
		
	def accessibleChildren(self):
		for prop in self.props:
			if not prop.accessibleChildren():
				return False
		return True
			
	def XMLSetup(self, node):
		Handler.XMLSetup(self, node)
		
		def splitAndClean(s):
			return tuple([s.strip() for s in s.split(',')])

		if self.name == None:
			if node.node.hasAttribute('name'):
				l = splitAndClean(node.node.getAttribute('name'))
				if node.node.getAttribute('adjective'):
					self.adjective = splitAndClean(node.node.getAttribute('adjective'))
					
				self.initWord(l)
	
	def XMLWrapup(self, node):
		Handler.XMLWrapup(self, node)
		if not self.hasProp('Normal'):
			try:
				f = node.getChild('ldesc')
				self.addProp(props.Normal(long=f.getValue()))
			except ScriptChildError:
				pass
		self.finalizeProps()
		
	def initWord(self, name):
		cls = self.__class__
			
		name = utils.makeTuple(name)
		self.word = self.wordClass(name)
		#: Word instance
		self.word.item = self
		
		if len(self.adjective) != 0:
			adjective = lib.Adjective(self.adjective)
			self.word.adjective = adjective
		
		self.name = self.word.name
		#: the name of Word is turned into instance name
		
		if cls.definite == None:
			self.definite = self.word.definite
		else:
			self.definite = cls.definite
			self.word.definite = cls.definite
			
		if cls.indefinite == None:
			self.indefinite = self.word.indefinite
		else:
			self.indefinite = cls.indefinite
			self.word.indefinite = cls.indefinite
		
	def updateAccessInfo(self, game):
		'''Update access info for self.'''
		cls = self.__class__
		cls.i = self # deprecate?
		cls.inst = self
		
		self.game = game
		
	def handleEvents(self, sentence):
		self.dispatchEvent(self.EVT_ITEM_HANDLE)
		current = self.owner
		while current != None:
			current.dispatchEvent(current.EVT_OWNED_ITEM_HANDLE)
			current = current.owner
		
	def intHandle(self, sentence, output):
		self.word.addWord('*self')
		self.handleEvents(sentence)
		
		if self.location != self.owner:
			if sentence[:2] == ('*touch', '*self'):
				if self.location != sentence.actor.location:
					sentence.actor.intMove(self.location)
					output.write(self.responses['notNear'] % self.location.name, False)
					
		try:
			self.handlePrivate(sentence,output)

			for prop in self.props:
				prop.intHandle(sentence, output)
		except OutputClosed:
			self.word.removeWord('*self')
			raise OutputClosed("")
		
		self.word.removeWord('*self')
		
	def __getattr__(self, name):
		try:
			return self.getProp(name)
		except PropError:
			pass
		raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, name))
		
	def moveToActor(self, output):
		'''Try to move the object to game.actor and write inline output accordingly.
		Raises PropError if self doesn't have the property Mobile.'''
		if self.owner == output.actor:
			return
		else:
			if not self.hasProp('Mobile'):
				raise PropError("Item is %s not mobile" % self.name)
			if output.actor.canAccess(self):
				self.Mobile.doTake()
				output.write('(first taking it)', False)
				
	def getProp(self, name):
		'''Get property from property list.
		
		name : str'''
		for prop in self.props:
			if prop.__class__.__name__ == name:
				return prop
		
		raise PropError("Item %s has no property %s." % (self.name, name))
		
	def hasProp(self, name):
		for prop in self.props:
			if prop.__class__.__name__ == name:
				return True
		
		return False
		
	def addProp(self, property):
		'''Add new property. finalizeProps should be called afterwards.
		
		prop : Property'''
		self.props += (property,)
		property.setParent(self)
		self.newprops.append(property)

	def finalizeProps(self):
		'''Finalize the current property list.'''
		self.finalizedprops = str(self.newprops)
		while self.newprops != []:
			self.newprops.pop().initProp()
			
	def removeProp(self, prop):
		'''Remove property.
		
		prop : Property - Property in the current propertylist.'''
		l = list(self.props)
		l.remove(prop)
		self.props = tuple(l)
		
	def move(self, dest):
		'''Move self to Item dest. This function should always be called to move objects
		around in the game world. You can override the default behaviour with an event
		listener.
		
		dest : Item'''
		try:
			output = self.ownerGame().output
		except GameError:
			output = None
		self.dispatchEvent(ItemMoveEvent(Item.EVT_MOVED, output, dest))
		self.dispatchEvent(ItemMoveEvent(Item.EVT_ITEM_RECEIVED, output, dest))
		self.intMove(dest)
		try:
			self.owner.inventory.remove(self)
		except AttributeError:
			pass
		self.owner = dest
		self.owner.inventory.append(self)
		
	def intMove(self, dest):
		try:
			output = self.ownerGame().output
		except GameError:
			output = None
		self.dispatchEvent(ItemMoveEvent(Item.EVT_INT_MOVED, output, dest))
		self.location = dest
		
	def canMove(self, other):
		try:
			if other.Mobile.movable:
				if other.owner == self:
					return True
		except AttributeError:
			pass
			
		return False
		
	def isIn(self, other):
		'''Returns true if self is inside other in the ownership tree. Ignores 
		accessibility modifiers'''
		if self.owner == None:
			return False
		elif self.owner == other:
			return True
		else:
			return self.owner.isIn(other)

	def canAccess(self, other):
		"""Called to check if other can self can access other in the game world. 
		Default implementation returns other.availableTo(self)
		
		other : Item
		
		returns : Boolean"""
		return other.availableTo(self)
			
	def availableTo(self, other):
		'''Used internally by canAccess to check self is available to other. Override
		to make item available.
		
		other : Item'''
		if not self.accessible or self.owner == None:
			return False
		elif not self.owner.accessibleChildren():
			return False
		elif self.owner == other.owner or self.owner == other:
			return True
		else:
			return other.canAccess(self.owner)
		return False

class Actor(Item):
	'''Class for player characters. Handles sentences for examining the surroundings, 
	moving, saving and loading the game.'''
	name = 'Player Character', 'player', 'yourself', 'self'
	pronoun = None
	
	WAIT = 'wait'
	
	responses = {
		'notADirection' : "%s is not a direction.",
		'noDirection' : "You should specify which direction you want to walk to.",
		'nothingHappens' : "You feel nothing unexpected.",
		'cantDo' : "You can't %s %s.",
		'itemUnavailable' : "You can't see anything like that here.",
		'verbKnown' : "I only understood that you want to %s something.",
		'unhandled' : "I don't know what that means.",
		'noViolence' : "Violence never solves anything.",
		WAIT : 'Time passes.',
		'saved' : "Saved!",
		'loaded' : "Loaded!"
	}
	
	LOOK = "look"
	'''Verb used to get a description of the player's surroundings.'''
	
	def unhandledSentence(self, sentence, output):
		if sentence[0] == '*verb':
			if sentence == 'z':
				self.write(output, self.WAIT)
			if sentence[0] == 'go':
				if len(sentence) == 2:
					output.write(self.responses['notADirection'] % (sentence[1].name))
				elif len(sentence) == 1:
					self.write(output, 'noDirection')

			if len(sentence) == 2:
				if sentence[1] == '*noun':
					if self.canAccess(sentence[1].item):
						if sentence[0] == 'touch':
							self.write(output, 'nothingHappens')
						elif sentence[0] == '*attack':
							self.write(output, 'noViolence')
						output.write(self.responses['cantDo'] % (sentence[0].name, sentence[1].item.definite))
					else:
						self.write(output, 'itemUnavailable')
			else:
				output.write(self.responses['verbKnown'] % sentence[0].name)
		
		self.write(output, 'unhandled')
		
	def input(self, output, sentence):
		output.actor = self
		sentence.actor = self
	
	def handlePrivate(self, sentence, output):
		Item.handlePrivate(self,sentence,output)
		self.handleMove(sentence, output)
		
		if sentence == self.LOOK:
			output.target = self.owner
			self.lookAround(output)
		elif sentence == 'save':
			self.game.pickle()
			self.write(output, 'saved')
		elif sentence == "restore":
			self.game.unpickle()
			self.write(output, 'loaded')
			
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
		
	def lookAround(self, output, short=False):
		'''Write the current room description.
		
		output : Output
		short : bool - Whether to write the short description of the room.'''
		if short:
			if self.owner.Normal.short == None:
				output.close()
			else:
				output.write(self.owner.Normal.getDesc("short", self.owner))
				
		else:
			output.write(self.owner.Normal.getLong(), obj = self.owner)
		
	def newLocation(self, output):
		'''Called to write description of a new location. If room has been visited before
		will write the short description.
		
		output : Output'''
		output.write('<b>' + self.owner.name + '</b>', False)

		if self.owner.visited:
			self.lookAround(output, True)
		else:	
			self.lookAround(output, False)

		self.owner.visited = True
			
	def getMoveDir(self, sentence):
		'''Get movement direction from sentence.
		
		sentence : Sentence'''
		if sentence == 'go *direction':
			return sentence[1]
		elif sentence == '*direction':
			return sentence[0]
			
		raise ValueError('Sentence "%s" has no movement direction.' % str(sentence))

from handler import HandlerEvent

class ItemMoveEvent(HandlerEvent):
	def __init__(self, type, output, destination):
		HandlerEvent.__init__(self, type, output)
		self.destination = destination

class Male(Item):
	pronoun = 'him'
	
class Female(Item):
	pronoun = "her"
	
def _addExit(self, event):
	self.exits[self.uninitedExits[event.target.__class__]] = event.target
	del self.uninitedExits[event.target.__class__]
	
class Room(Item):
	'''instances attributes:
		exits : dict - Dict containing room's exits. Key is Direction and value is a Room
		or a Door.'''
	NO_EXIT = 'noExit'
	ONLY_EXIT = 'onlyExit'
	SEE_EXITS = "seeExits"
	responses = {
		NO_EXIT : "You see no exit that way.",
		ONLY_EXIT : "The only exit leads %s.",
		SEE_EXITS : "You see exits leading %s."
	}
	
	def __init__(self):
		Item.__init__(self)
		self.exits = getattr(self, 'exits', {})
		self.visited = False
		self.uninitedExits = {}
		
	def hasExit(self, d):
		'''Return true if room has exit d.
		
		d : Direction'''
		for exit in self.exits:
			if d == exit:
				return True

		return False

	def XMLWrapup(self, node):
		Item.XMLWrapup(self, node)
		try:
			f = node.getChild('exits')
			
			for child in f.children:
				e = child.getValue()
				if type(e) == handler.HandlerMeta:
					if e.inst == None:
						e.addClassEventListener(e.EVT_INIT, (self, _addExit))
						self.uninitedExits[e] = child.node.tagName 
					else:
						self.exits[child.node.tagName] = e.inst
				else:
					self.exits[child.node.tagName] = e
		except ScriptError:
			pass
			

	def exit(self, d):
		'''Return exit in direction d.
		
		d : Direction'''
		for exit in self.exits:
			if d == exit:
				return self.exits[exit]
				
	def tryAccess(self, d, output):
		'''Return exit to the direction d or writes output.
		
		d : Direction
		output : Output'''
		x = self.exit(d)

		if type(x) == str or type(x) == unicode:
			output.write(x)
		elif x:
			x = x.access(d, output)
			return x
		else:
			s = self.responses[self.NO_EXIT]
			l = len(self.exits.keys())
			if l > 0:
				if l == 1:
					s += " " + self.responses[self.ONLY_EXIT] % self.exits.keys()[0]
				else:
					s += ' ' + self.exitString()
			output.write(s)
			
	def exitString(self):
		s = self.responses[self.SEE_EXITS] % utils.naturalJoin(self.exits.keys(), ', ', ' and ')
		return s
		
	def access(self, d, output):
		'''Return exit from the direction d or write output.
		
		d : Direction
		output : Output'''
		return self
		
class Door(Room):
	NO_KEY = 'noKey'
	responses = {
		NO_KEY : "The door is locked and you don't have a key."
	}
	
	def __init__(self):
		Item.__init__(self)
		self.exits = getattr(self, 'exits', {})
			
	def tryAccess(self, d, output):
		pass
		
	def access(self, d, output):
		if self.hasProp('Closable'):
			if self.Closable.closed:
				if self.Closable.canOpen():
					self.Closable.inlineOpen(output)
				else:
					self.write(output, self.NO_KEY)
				
		return self.exit(d).access(d, output)
		
	def availableTo(self, other):
		for exit in self.exits:
			if other.owner == self.exits[exit]:
				return True
				
class Location(Item):
	wordClass = lib.Location
	def XMLWrapup(self, node):
		Item.XMLWrapup(self, node)
		for item in self.inventory:
			item.move(self.owner)
			item.intMove(self)
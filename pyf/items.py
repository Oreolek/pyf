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

from handler import Handler, HandlerMeta
from errors import *

import lib, copy

class PrivateAccessor(object):
	'''A simple proxy for private variables.'''
	def __init__(self, name):
		self.name = name
	def __get__(self, instance, owner):
		return getattr(instance, self.name)
			
	def __set__(self, instance, value):
		return setattr(instance, self.name, value)

class WordAccessor(PrivateAccessor):
	'''A simple proxy between an object and its word.'''
	def __get__(self, instance, owner):
		return getattr(instance.word, self.name)
	def __set__(self, instance, value):
		return setattr(instance.word, self.name, value)
		
class ItemMeta(HandlerMeta):
	wordAccessors = ('name','definite','indefinite')
	def __init__(cls, *args, **kwargs):
		HandlerMeta.__init__(cls, *args, **kwargs)
		for name in ItemMeta.wordAccessors:
			if hasattr(cls, name):
				s = getattr(cls, name)
				setattr(cls, name, WordAccessor(name))
				setattr(cls, '_%s' % name, s)
		
	def __call__(cls, *args, **kwargs):
		self = HandlerMeta.__call__(cls, *args, **kwargs)
		for name in ItemMeta.wordAccessors:
			n = '_%s' % name 
			if hasattr(cls, n):
				setattr(self, name, getattr(cls, n))
			
		return self

		
class Item(Handler):
	'''Item is the base class for all the items in PyF game world.'''
	
	__metaclass__ = ItemMeta
	
	EVT_MOVED = 'evtMoved'
	'''Fired brefore item is moved around in the game world.'''
	EVT_ITEM_OWNER_MOVED = 'evtItemOwnerMoved'
	'''TODO'''
	EVT_INT_MOVED = 'evtIntMoved'
	'''Fired before item is moved internally to a new location.'''
	EVT_ITEM_OWNER_INT_MOVED = "evtItemOwnerIntMoved"
	'''TODO'''
	EVT_ITEM_RECEIVED = "evtItemReceived"
	'''Fired before an item dest is added to item's inventory.'''
	EVT_ITEM_INT_RECEIVED = "evtItemIntReceived"
	'''Fired before an item is internally moved to item.'''
	EVT_ITEM_LOST = "evtItemLost"
	'''Fired before an item is moved away from item.'''
	EVT_ITEM_INT_LOST = "evtItemIntLost"
	'''Fired before item is internally moved away from its location.'''
	EVT_HANDLE = "evtHandle"
	'''Fired before item is taken through the default input handling process.'''
	EVT_OWNED_ITEM_HANDLE = "evtOwnedItemHandle"
	'''Fired before an owned item is taken through the default input handling process.'''
	
	EVT_INIT = "evtInit"
	'''Fired after the class has been instantiated.'''
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
	
	inst = None
	
	# default values
	adjective = ()
	'''tuple - Strings in tuple are converted into adjectives for the Word
	name. Adjectives can be used to match words more accurately.'''
	props = ()
	'''tuple - props to attach to the Item during instance 
	construction. Property instances are deepcopied during construction.'''
	available = True
	'''bool - Controls whether the item is accessible in the game world. This
	can be used to hide the object regardless of its real location in the game world.'''
	owner = None
	'''Item instance - Owner of this item in the game world.'''
	definite = None
	'''str - Definite name of this item, eg. "the book".'''
	indefinite = None
	'''str - Indefinite name of this item, eg. "a book".'''
	
	wordClass = lib.Noun
	'''The Word class in which the name is instantiated.'''

	needTravel = False
	'''Used to indicate that the player needs to travel to this in order to interact
	with its objects.'''
	locationName = None
	'''Displayed as the name when traveling to this item.'''
	
	listeners = {}
	
	def __init__(self):
		self.word = self.wordClass()
		self.word.item = self
		Handler.__init__(self)

		cls = self.__class__
		cls.inst = self
		self.game = None
		
		
		self.props = ()
		self.inventory = inventory.Inventory()
		'''list - contains all the items this item owns'''
		
		self.newprops = []
		self.available = cls.available
		
		if cls.owner != None:
			self.owner = None
			self.move(cls.owner)
		else:
			self.owner = None
			
		if cls.location != None:
			self.intMove(cls.location)
		else:
			self.location = None

		props = cls.props
		if props.__class__ != tuple:
			props = (props,)

		for prop in props:
			prop = prop.clone()
			self.addProp(prop)
			
		self.finalizeProps()
		self.dispatchEvent(self.EVT_INIT)
		
	def __eq__(self, other):
		if type(self) is other:
			return True
		else:
			return id(self) == id(other)
			
	@property
	def accessible(self):
		'''Proxy for self.accessible'''
		return self.available
		
	@accessible.setter
	def accessible(self, value):
		self.available = value

	def accessibleChildren(self):
		return True
		
	def XMLSetup(self, node):
		Handler.XMLSetup(self, node)
		

		if self.name == None:
			def splitAndClean(s):
				return tuple([s.strip() for s in s.split(',')])
				
			if node.node.hasAttribute('name'):
				l = splitAndClean(node.node.getAttribute('name'))
				self.name = l
			if node.node.hasAttribute('definite'):
				self.definite = node.node.getAttribute('definite')
			if node.node.hasAttribute('indefinite'):
				self.indefinite = node.node.getAttribute('indefinite')
				
			if node.node.getAttribute('adjective'):
				a = splitAndClean(node.node.getAttribute('adjective'))
				self.adjective = lib.Adjective(a)
	
	def XMLWrapup(self, node):
		Handler.XMLWrapup(self, node)
		if not props.Normal in self.props:
			try:
				f = node.getChild('ldesc')
				self.addProp(props.Normal(long=f.getValue()))
			except ScriptChildError:
				pass
		self.finalizeProps()
		
	def removeWord(self):
		self.ownerGame.lib.remove(self.word)
		word = self.word
		self.word = None
		self.definite = None
		self.indefinite = None
		
	def updateAccessInfo(self, game):
		'''Update access info for self.'''
		cls = self.__class__
		cls.inst = self
		
		self.game = game
	
	@property
	def absLocation(self):
		if self.location == None:
			return self
		elif self.location.needTravel:
			return self.location
		else:
			return self.location.absLocation
			
		
	def handleEvents(self, sentence):
		self.dispatchEvent(self.EVT_HANDLE)
		current = self
		while current != None:
			if current == sentence.actor:
				break
			elif current == self:
				current = current.owner
				continue

			current.dispatchEvent(current.EVT_OWNED_ITEM_HANDLE)
			current = current.owner
		
	def intHandle(self, sentence, output):
		self.word.addWord('*self')
		try:
			self.handleEvents(sentence)
		
			s = self.absLocation
			if s != sentence.actor.absLocation:
				if s.needTravel:
					if sentence[:2] == ('*closeverb', '*self'):
						sentence.actor.intMove(self.absLocation)
						output.write(sentence.actor.responses['notNear'] % s.locationName, False)
					
			self.handlePrivate(sentence,output)

			for prop in self.props:
				prop.intHandle(sentence, output)
		except OutputClosed, e:
			self.word.removeWord('*self')
			raise e
		except SkipHandle:
			pass
		
		self.word.removeWord('*self')
		
	def __getattr__(self, name):
		try:
			return self.getProp(name)
		except PropError:
			raise AttributeError("%s instance has no attribute '%s'" % (self.__class__.__name__, name))
		
	def moveToActor(self, output):
		'''Try to move the object to game.actor and write inline output accordingly.
		Raises PropError if self doesn't have the property Mobile.'''
		if self.owner == output.actor:
			return
		else:
			if not props.Mobile in self.props:
				raise PropError("Item is %s not mobile" % self.name)
			if output.actor.canAccess(self):
				self.Mobile.doTake()
				output.write('(first taking it)', False)
				
	def getProp(self, name):
		'''Get property from property list.
		
		name : str'''
		for prop in self.props:
			if prop.name == name:
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
			self.newprops.pop().init()
			
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
			output = self.ownerGame.actor.output
		except GameError:
			output = None
		self.dispatchEvent(ItemMoveEvent(self.EVT_MOVED, output, self.owner, dest, self))
		if dest != None:
			dest.dispatchEvent(ItemMoveEvent(self.EVT_ITEM_RECEIVED, output, self.owner, dest, self))

		if self.owner != None:
			self.owner.dispatchEvent(ItemMoveEvent(self.EVT_ITEM_LOST, output, self.owner, dest, self))
			
		self.intMove(dest)
			
		if self.owner != None:
			self.owner.inventory.remove(self)

		self.owner = dest
		
		if self.owner != None:
			self.owner.inventory.append(self)
			
	def intMove(self, dest):
		try:
			output = self.ownerGame.actor.output
		except GameError:
			output = None
		self.dispatchEvent(ItemMoveEvent(self.EVT_INT_MOVED, output, self.location, dest, self))
		if self.location != None:
			self.location.dispatchEvent(ItemMoveEvent(self.EVT_ITEM_INT_LOST, output, self.location, dest, self))
		if dest != None:
			dest.dispatchEvent(ItemMoveEvent(self.EVT_ITEM_INT_RECEIVED, output, self.location, dest, self))
		
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
		
		@type	other:	Item
		
		@rtype	: Boolean"""
		return other.availableTo(self)
			
	def availableTo(self, other):
		'''Used internally by canAccess to check self is available to other.
		
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


from handler import HandlerEvent

class ItemMoveEvent(HandlerEvent):
	def __init__(self, type, output, source, destination, item):
		self.destination = destination
		'''Where item is being moved to.'''
		self.source = source
		'''Where item is being moved from.'''
		self.item = item
		'''What item is being moved. Does NOT always equal event.target.'''
		HandlerEvent.__init__(self, type, output)

class Male(Item):
	'''Simple deviation of Item that defines a pronoun and a different word class.'''
	wordClass = lib.Person
	pronoun = 'him'
	
class Female(Item):
	'''Simple deviation of Item that defines a pronoun and a different word class.'''
	wordClass = lib.Person
	pronoun = "her"
	
class Animal(Item):
	'''Simple deviation of Item that uses a different word class.'''
	wordClass = lib.Animal
	
class Creature(Item):
	'''Simple deviation of Item that uses a different word class.'''
	wordClass = lib.Creature
	
def _addExit(self, dir, event):
	self.exits[dir] = event.target
	
def _actorMove(self, receive, event):
	if type(event.target) == Actor:
		if receive:
			self.dispatchEvent(self.EVT_ENTERED)
		else:
			self.dispatchEvent(self.EVT_LOST)
	
class Room(Item):
	'''Superclass for items with exits.'''
	
	EVT_ENTERED = "evtEntered"
	'''Fired before actor enters room.'''
	EVT_LEFT = "evtLeft"
	'''Fired before actor leaves room.'''
		
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
		self.addEventListener(self.EVT_ITEM_RECEIVED, (self, True, _actorMove))
		self.addEventListener(self.EVT_ITEM_LOST, (self, False, _actorMove))
		
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
				if type(e) == ItemMeta:
					if e.inst == None:
						e.addClassEventListener(e.EVT_INIT, (self, child.node.tagName, _addExit))
					else:
						self.exits[child.node.tagName] = e.inst
				else:
					self.exits[child.node.tagName] = e
		except ScriptChildError:
			pass
			

	def exit(self, d):
		'''Return exit in direction d.
		
		d : Direction'''
		for exit in self.exits:
			if d == exit:
				return self.exits[exit]
		raise KeyError("Exit '%s' not found in %s" % (d, self))
				
	def tryAccess(self, d, output):
		'''Return exit to the direction d or writes output.
		
		d : Direction
		output : Output'''
		try:
			x = self.exit(d)
		except KeyError:
			s = self.responses[self.NO_EXIT]
			l = len(self.exits.keys())
			if l > 0:
				if l == 1:
					s += " " + self.responses[self.ONLY_EXIT] % self.exits.keys()[0]
				else:
					s += ' ' + self.exitString()
			output.write(s)

		if type(x) == str or type(x) == unicode:
			output.write(x)
		elif x:
			x = x.access(d, output)
			return x
			
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
		if props.Openable in self.props:
			if self.Openable.closed:
				self.Openable.inlineOpen(output)
				
		return self.exit(d).access(d, output)
		
	def availableTo(self, other):
		for exit in self.exits:
			if other.owner == self.exits[exit]:
				return True
		return False
				
class Location(Item):
	wordClass = lib.Location
	needTravel = True
	def XMLWrapup(self, node):
		Item.XMLWrapup(self, node)
		for item in self.inventory:
			item.move(self.owner)
			item.intMove(self)
			
	@property
	def locationName(self):
		return self.name
			
from actor import *

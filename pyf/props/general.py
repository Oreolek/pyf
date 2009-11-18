'''Defines properties, which are commonly used in IF, like describing and moving
things.'''

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

from pyf.props import Property, SwitchEvent
import containers
import  string

class Normal(Property):
	'''Display descriptions for objects.'''
	EVT_EXAMINED = 'evtExamined'
	
	def __init__(self, long=None, short=None, inv=None):
		Property.__init__(self)
		self.long = long
		'''Long description of the object.'''
		self.short = short
		'''Short description of the object. Typically shown as part of object owner's 
		long description.'''
		self.inv = inv
		'''Invoked when player examines inventory.'''
		
	def handle(self, sentence, output):
		if sentence == ('examine', '*self'):
			self.examine(output)
		
	def examine(self, output):
		output.write(self.getLong())
		
	def doExamine(self):
		self.dispatchEvent(self.EVT_EXAMINED)
		
	def init(self):
		if self.short == None:
			self.short = self.owner.indefinite
		if self.inv == None:
			self.inv = self.owner.indefinite
		
	def removeShortDesc(self, s):
		return s.remove(self.descToken(), '')
		
	def descToken(self):
		return '{' + self.owner.name + '}'
		
	def getDesc(self, t):
		s = self.getFlat(t)
		
		return s
		
	def getFlat(self, t):
		if t == 'long':
			self.doExamine()
		out = getattr(self, t)
			
		if out == None:
			raise AttributeError("Normal property's description '%s' is unset" % t)
			
		s = out
		for prop in self.owner.props:
			if prop != self:
				e = prop.getDesc(t, s)
				if e != None:
					s += (' ' + e)

		return self.fillDescription(s, self.owner)
			
	def getLong(self):
		self.doExamine()
		return self.getFlat('long')
		
	def fillDescription(self, s, target):
		d = {}
		for item in target.inventory:
			try:
				d[item.name] = item.Normal.getFlat('short')
				if d[item.name] == None:
					d[item.name] = ''
			except AttributeError:
				pass
		
		f = DescFormatter()
		return f.format(s, d)
		
	def __nonzero__(self):
		return True
		
	def shortest(self):
		if self.inv != None:
			return self.inv
		else:
			return self.owner.name
			
class DescFormatter(string.Formatter):
	def get_value(self, key, args, kwargs):
		if key not in args[0]:
			return ''
		else:
			s = args[0][key]
			try:
				s = s()
			except TypeError:
				pass
			return s
		
class Mobile(Property):
	"""Defines item as something that actor can move around."""
	EVT_TAKEN = 'evtTaken'
	'''Fired before an actor takes owner.'''
	EVT_DROPPED = 'evtDropped'
	'''Fired before an actor drops owner.'''
	
	TAKEN = "mobileTaken"
	'''Printed when player succesfully takes object.''' 
	DROPPED = "mobileDropped"
	'''Printed when player succesfully drops object.''' 
	ALREADY_TAKEN = "mobileAlreadyTaken"
	'''Printed if player tries to take an object when they're already carrying it. ''' 
	ALREADY_DROPPED = "mobileAlreadyDropped"
	'''Printed if player tries to drop an object when they're not carrying it. ''' 
	
	CHILDREN_UNACCESSIBLE = 'mobileChildrenUnaccessible'
	'''Prints an error message when player attempts to drop this object in a room where it
	might get lost.'''
	NOT_TAKEABLE = 'mobileNotTakeable'
	'''Printed when player attempts to take an object set as untakeable.'''
	NOT_DROPPABLE = 'mobileNotDroppable'
	'''Printed when player attempts to drop an object set as undroppable.'''
	PUSHED = 'pushed'
	'''Prints output when player pushes object into a location in the current room.'''
	ALREADY_PUSHED = 'alreadyPushed'
	'''Prints output when the object is already where player is trying to push it.'''
	
	responses = {
		TAKEN : 'Taken.',
		DROPPED: 'Dropped.',
		ALREADY_TAKEN : "You're already carrying [self.definite].",
		ALREADY_DROPPED : "You're not carrying [self.definite].",
		CHILDREN_UNACCESSIBLE: 'If you drop [self.definite] here you might never find [self.pronoun] again.',
		NOT_TAKEABLE : "That's not something you want to be carrying around.",
		NOT_DROPPABLE : "That's not something you want to leave lying around.",
		PUSHED : "You push [self.definite] [nouns[1].name].",
		ALREADY_PUSHED : "[self.definite] is already pushed [nouns[0].name]."
	}
	
	def __init__(self, droppable=True, takeable=True, movable=True, autoDescribe=True):
		Property.__init__(self)
		self.droppable=droppable
		self.takeable = takeable
		self.dropped = False
		self.movable = movable
		self.autoDescribe = autoDescribe
		
	def handle(self, sentence, output):
		if sentence == ('take', '*self'):
			self.take(output)
		elif sentence == ('drop', '*self'):
			self.drop(output)
		elif sentence == ("push", '*self', '*location'):
			self.push(sentence[2].item, output)
			
	def push(self, location, output):
		if self.movable:
			if self.owner.owner != output.actor:
				if self.owner.location != location:
					self.doPush(location)
					output.write(self.responses[self.PUSHED])
				else:
					output.write(self.responses[self.ALREADY_PUSHED])
				
	def doPush(self, location):
		self.owner.intMove(location)
		
	def take(self, output):
		if self.takeable:
			if self.owner.owner != output.actor:
				self.doTake()
				self.write(output, self.TAKEN)
			else:
				self.write(output, self.ALREADY_TAKEN)
		else:
			self.write(output, self.NOT_TAKEABLE)
			
	def doTake(self):
		self.dispatchEvent(Mobile.EVT_TAKEN)
		self.owner.move(self.owner.game.actor)		
		
	def drop(self, output):
		if self.droppable:
			actor = output.actor
			if self.owner.owner == actor:
				if not actor.owner.accessibleChildren():
					self.write(output, self.CHILDREN_UNACCESSIBLE)
				else:
					self.doDrop()
					self.write(output, self.DROPPED)
			else:
				self.write(output, self.ALREADY_DROPPED)
		else:
			self.write(output, self.NOT_DROPPABLE)
				
	def doDrop(self):
		self.dispatchEvent(Mobile.EVT_DROPPED)	
		self.dropped = True
		self.owner.move(self.owner.game.actor.owner)
		
def _openableHandle(self, event):
	if self.closed:
		raise SkipHandle()

def _opened(self, event):
	if self.locked:
		if self.keyAvailable():
			self.doUnlock()
			event.output.write(self.responses[self.UNLOCKED_INLINE], False, obj = self)
		else:
			event.output.write(self.responses[self.NO_KEY], obj = self)

class Openable(Property):
	'''Defines something that can be closed and opened.'''
	
	EVT_STATE_OPEN = "evtStateOpen"
	'''Fired before object's open state changes.'''

	EVT_STATE_LOCKED = 'evtStateLocked'
	'''Fired before object's locked state changes.'''
	
	OPENED = "opened"
	CLOSED = "closed"
	UNLOCKED = 'unlocked'
	LOCKED = 'locked'
	ALREADY_UNLOCKED = 'alreadyUnlocked'
	ALREADY_LOCKED = 'alreadyLocked'
	ALREADY_OPEN = 'alreadyOpen'
	ALREADY_CLOSED = 'alreadyClosed'
	UNLOCKED_INLINE = 'unlockedInline'
	OPENED_INLINE = 'openedInline'
	CLOSED_INLINE = 'closedInline'
	NO_KEY = 'noKey'
	CURRENTLY_CLOSED = 'currentlyClosed'
	CURRENTLY_OPEN = 'currentlyOpen'
	
	responses = {
		OPENED: 'You finish opening [self.definite].',
		ALREADY_OPEN: "It's already open.",
		CLOSED: 'You finish closing [self.definite].',
		ALREADY_CLOSED : "It's already closed.",
		UNLOCKED: 'You finish unlocking [self.definite].',
		ALREADY_UNLOCKED: "It's already unlocked.",
		LOCKED: 'You finish locking [self.definite].',
		ALREADY_LOCKED: "It's already locked.",
		UNLOCKED_INLINE:'(first unlocking [self.definite])',
		OPENED_INLINE: '(first opening [self.definite])',
		CLOSED_INLINE: '(first closing [self.definite])',
		NO_KEY : "You don't have the key.",
		CURRENTLY_CLOSED : "It's closed.",
		CURRENTLY_OPEN : "It's open."
	}
	
	def __init__(self, closed=True, locked=False, key=None):
		Property.__init__(self)
		self.closed = closed
		self.locked = locked
		self.key = key
		
		self.addEventListener(self.EVT_STATE_OPEN, (self, _opened))
		
	def init(self):
		self.owner.addEventListener(self.owner.EVT_OWNED_ITEM_HANDLE, (self, _openableHandle))
		
	def handle(self, sentence, output):
		if sentence == ('open', '*self'):
			self.open(output)
		elif sentence == ('close', '*self'):
			self.close(output)
		elif self.key != None:
			if sentence == ('unlock', '*self'):
				self.unlock(output)
			elif sentence == ('lock', '*self'):
				self.lock(output)
		
	def getDesc(self, type, desc):
		if type == 'long':
			if self.closed:
				return self.responses[self.CURRENTLY_CLOSED]
			else:
				return self.responses[self.CURRENTLY_OPEN]
	
	def accessibleChildren(self):
		return self.closed == False
		
	def unlock(self, output):
		if not self.locked:
			self.write(output, self.ALREADY_UNLOCKED)
		elif self.keyAvailable():
			self.doUnlock()
			self.write(output, self.UNLOCKED)
		else:
			self.write(output, self.NO_KEY)

	def doUnlock(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_LOCKED), False)
		self.locked = False
		
	def canOpen(self):
		if self.locked:
			if self.keyAvailable():
				return True
			else:
				return False
		else:
			return False
				
	def lock(self, output):
		if self.locked:
			self.write(output, self.ALREADY_LOCKED)
		elif self.keyAvailable():
			if not self.closed:
				self.doClose()
				self.write(output, self.CLOSED_INLINE, False, obj = self.owner)
			self.doLock()
			self.write(output, self.LOCKED)
		else:
			self.write(output, self.NO_KEY)
			
	def doLock(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_LOCKED), True)
		self.locked = True		
			
	def keyAvailable(self):
		if self.key != None:
			if self.owner.game.actor.canAccess(self.key):
				return True
			else:
				return False

	def open(self, output):
		if self.closed:
			if self.locked:
				if self.keyAvailable():
					self.doUnlock()
					self.write(output, self.UNLOCKED_INLINE, False, obj = self.owner)
			self.doOpen()
			out = self.responses[self.OPENED]
			
			if containers.Container is self.owner.props:
				s = self.owner.Container.getDesc('Openable', '')
				if s != None:
					s = self.owner.Normal.fillDescription(s, self.owner)
					out += ' ' + s
				
			output.write(out)
		
		else:
			self.write(output, self.ALREADY_OPEN)
			
	def inlineOpen(self, output):
		if self.closed:
			self.doOpen()
			self.write(output, self.OPENED_INLINE, False, obj = self.owner)
		else:
			self.write(output, self.ALREADY_OPEN)
			
	def doOpen(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_OPEN, True))
		self.closed = False
		
			
	def close(self, output):
		if not self.closed:
			self.doClose()
			self.write(output, self.CLOSED)
		else:
			self.write(output, self.ALREADY_CLOSED)
			
	def doClose(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_OPEN, False))
		self.closed = True
		
def _darkExamined(self, event):
	if not self.lit:
		self.owner.visited = False
		self.write(event.output, self.DARKENED)
		
def _darkOwnedItemHandle(self, event):
	if not self.lit:
		self.write(event.output, self.HANDLE_DARK)
		
class Dark(Property):
	"""Disallows handling objects that are in a dark container."""
	EVT_STATE_LIGHT = 'evtStateLit'
	'''Fired before object's light state changes. Not fired
	if the object is lit by player's light source.'''
	
	LIT = 'darkLit'
	DARKENED = 'darkDarkened'
	HANDLE_DARK = "darkHandleDark"
	
	responses = {
		DARKENED : "It's dark in here.",
		HANDLE_DARK : "There's not enough light.",
	}
	
	def __init__(self, light=False):
		Property.__init__(self)
		self.light = light
		
	def init(self):
		self.owner.Normal.addEventListener(Normal.EVT_EXAMINED, (self, _darkExamined))
		self.owner.addEventListener(self.owner.EVT_OWNED_ITEM_HANDLE, (self, _darkOwnedItemHandle))
		
	def accessibleChildren(self):
		return self.lit
		
	def doLight(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_LIGHT), True)
		self.light = True
			
	def doDarken(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_LIGHT), False)
		self.light = False
		
	@property
	def lit(self):
		for item in self.ownerGame.inventory:

			if LightSource in item.props:
				if item.LightSource.on:
					if self.owner.canAccess(item):
						if not item.LightSource.inverse:
							return True
						else:
							return False
		
		return self.light
		
class LightSource(Property):
	'''When item is in a dark room, light it.'''
	def __init__(self, on=True, inverse=False):
		Property.__init__(self)
		self.on = on
		'''Whether it's currently emitting light.'''
		self.inverse = inverse
		'''True if item should suck light from container rather than emit it.'''
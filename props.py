
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

import handler, states, utils, copy
from errors import *

class SwitchEvent(handler.HandlerEvent):
	'''Used for events that are fired by a simple switch in the object's state.'''
	def __init__(self, type, value):
		handler.HandlerEvent.__init__(self, type, None)
		self.value = value
		#: value that the switch is being changed to

class Property(handler.Handler):
	def __init__(self, responses={}):
		self.responses = getattr(self, 'responses').copy()
		self.responses.update(responses)
		
		handler.Handler.__init__(self)
		self.name = self.__class__.__name__
		
	def move(self, dest):
		dest.addProp(self)
		
	def accessibleChildren(self):
		return True
		
	def clone(self):
		f = copy.copy(self)
		f.responses = copy.copy(self.responses)
		f.responses.parent = self
		
		f.handlers = copy.copy(self.handlers)
		f.handlers.parent = self
		return f
		
	def setParent(self, parent):
		'''Initialize parent as the owner of this property.'''
		self.owner = parent
		
	def XMLSetup(self, node):
		handler.Handler.XMLSetup(self, node)
		for n in node.children:
			if n.node.nodeName in self.__dict__:
				try:
					self.__dict__[n.node.nodeName] = n.getValue()
				except ScriptClassError:
					pass

	def getDesc(self, type, desc):
		return ''
		
	def ownerGame(self):
		'''Returns the game of the Item this property belongs to.'''
		if self.owner == None:
			raise PropError("Property %s's owner is set to None" % self.__class__.__name__)
		return self.owner.game
		
	def initProp(self):
		'''Called after the property list has been finalized to allow final access
		to other properties' attributes.'''
		
	def handleScript(self, sentence, output):
		pass

import string
import game

class Normal(Property):
	EVT_EXAMINED = 'normalExamined'
	
	def __init__(self, long=None, short=None, inv=None, responses={}):
		Property.__init__(self, responses)
		self.long = long
		self.short = short
		self.inv = inv
		
	def handle(self, sentence, output):
		if sentence == ('examine', '*self'):
			self.examine(output)
		
	def examine(self, output):
		self.doExamine()
		output.write(self.getLong(), obj=self.owner)
		
	def doExamine(self):
		self.dispatchEvent(self.EVT_EXAMINED)
		
	def initProp(self):
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
			'''try:
				s = self.getScript()
				if t in s:
					out = s.getChild(t).getValue()
					
			except ScriptError:
				pass'''
		
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
		
def _wearableMoved(self, event):
	if event.output != None:
		if self.worn:
			self.doStrip()
			self.write(event.output, self.STRIPPED_INLINE, False)

class Wearable(Property):
	EVT_STATE_WORN = "evtStateWorn"
	'''Fired every time the object's worn state is changed'.'''
	
	STRIPPED = 'wearableStripped'
	WORN = 'wearableWorn'
	ALREADY_STRIPPED = 'wearableAlreadyStripped'
	ALREADY_WORN = 'wearableAlreadyWorn'
	STRIPPED_INLINE = 'wearableStrippedInline'
	INV_WORN = 'wearableInvWorn'
	
	responses = {
		STRIPPED: "You finish taking [self.definite] off.",
		ALREADY_STRIPPED : "You're not wearing [self.definite].",
		WORN: "You finish putting [self.definite] on.",
		ALREADY_WORN: "You're already wearing [self.definite].",
		STRIPPED_INLINE: '(first taking [self.definite] off)',
		INV_WORN : "(worn)",
		'wearableCurrentlyWearing' : "You're currently wearing it."
		
	}
	
	def __init__(self, worn=False, responses={}):
		Property.__init__(self, responses)
		self.worn = worn
		
	def handle(self, sentence, output):
		if sentence == ('strip', '*self'):
			self.strip(output)
		elif sentence == ('take', '*self', 'off'):
			self.strip(output)
		elif sentence == ("dress", '*self'):
			self.dress(output)
		elif sentence == ("put", '*self', 'on'):
			self.dress(output)
		
	def getDesc(self, type, desc):
		if type == 'long':
			if self.worn:
				return self.responses['wearableCurrentlyWearing']
		elif type == 'inv':
			if self.worn:
				return self.responses[self.INV_WORN]
		
	def initProp(self):
		self.owner.addEventListener(items.Item.EVT_MOVED, (self, _wearableMoved))
		
	def doStrip(self):
		self.dispatchEvent(SwitchEvent(Wearable.EVT_STATE_WORN, False))
		self.worn = False
		
	def strip(self, output):
		if not self.worn:
			self.write(output, self.ALREADY_STRIPPED)
		else:
			self.doStrip()
			self.write(output, self.STRIPPED)
		
	def doWear(self):
		self.dispatchEvent(SwitchEvent(Wearable.EVT_STATE_WORN, True))
		self.worn = True

	def dress(self, output):
		if self.worn:
			self.write(output, self.ALREADY_WORN)
		else:
			self.owner.moveToActor(output)
			self.doWear()
			self.write(output, self.WORN)

class Mobile(Property):
	EVT_TAKEN = 'evtMobileTaken'
	'''Fired every time the player takes the object.'''
	EVT_DROPPED = 'evtMobileDropped'
	'''Fired every time the player drops the object.'''
	
	TAKEN = "mobileTaken"
	DROPPED = "mobileDropped"
	ALREADY_TAKEN = "mobileAlreadyTaken"
	ALREADY_DROPPED = "mobileAlreadyDropped"
	
	CHILDREN_UNACCESSIBLE = 'mobileChildrenUnaccessible'
	NOT_TAKEABLE = 'mobileNotTakeable'
	NOT_DROPPABLE = 'mobileNotDroppable'
	
	responses = {
		TAKEN : 'Taken.',
		DROPPED: 'Dropped.',
		ALREADY_TAKEN : "You're already carrying it.",
		ALREADY_DROPPED : "You're not carrying it.",
		CHILDREN_UNACCESSIBLE: 'If you drop it here you might never find it again.',
		NOT_TAKEABLE : "That's not something you want to be carrying around.",
		NOT_DROPPABLE : "That's not something you want to leave lying around."
	}
	
	def __init__(self, droppable=True, takeable=True, movable=True, autoDescribe=True, responses={}):
		Property.__init__(self, responses)
		self.droppable=droppable
		self.takeable = takeable
		self.dropped = False
		self.autoDescribe = autoDescribe
		
	def handle(self, sentence, output):
		if sentence == ('take', '*self'):
			self.take(output)
		elif sentence == ('drop', '*self'):
			self.drop(output)
		
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

class Openable(Property):
	EVT_STATE_OPEN = "evtStateOpen"
	'''Fired when object's open state changes.'''

	EVT_STATE_LOCKED = 'evtStateLocked'
	'''Fired when object's locked state changes.'''
	
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
	CURRENTLY_OPEN = 'currentlyClosed'
	
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
	
	def __init__(self, closed=True, locked=False, key=None, responses={}):
		Property.__init__(self, responses)
		self.closed = closed
		self.locked = locked
		self.key = key
		
	def handle(self, sentence, output):
		if sentence == ('open', '*self'):
			self.open(output)
		elif sentence == ('close', '*self'):
			self.close(output)
		elif sentence == ('unlock', '*self'):
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
		return self.closed
		
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
			return True
				
	def lock(self, output):
		if self.locked:
			self.write(output, self.ALREADY_LOCKED)
		elif self.keyAvailable():
			if not self.closed:
				self.doClose()
				self.write(output, self.CLOSED_INLINE, False)
			self.doLock()
			self.write(output, self.LOCKED)
		else:
			self.write(output, self.NO_KEY)
			
	def doLock(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_LOCKED), True)
		self.locked = True		
			
	def keyAvailable(self):
		if self.owner.game.actor.canAccess(self.key):
			return True
		else:
			return False

	def open(self, output):
		if self.closed:
			if self.locked:
				if self.keyAvailable():
					self.doUnlock()
					self.write(output, self.UNLOCKED_INLINE, False)
			self.doOpen()
			out = self.responses[self.OPENED]
			
			if self.owner.hasProp('Container'):
				s = self.owner.Container.getDesc('Openable', '')
				if s != None:
					s = self.owner.Normal.fillDescription(s, self.owner)
					out += ' ' + s
				
			output.write(out, obj=self.owner)
		
		else:
			self.write(output, self.ALREADY_OPEN)
			
	def inlineOpen(self, output):
		if self.closed:
			if self.locked:
				if self.keyAvailable():
					self.doUnlock()
					self.write(output, self.UNLOCKED_INLINE, False)
			self.doOpen()
			self.write(output, self.OPENED_INLINE, False)
		else:
			self.write(output, self.ALREADY_OPEN)
			
	def doOpen(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_OPEN), True)
		self.closed = False
		
	@property
	def open(self):
		return self.closed == False
			
	def close(self, output):
		if not self.closed:
			self.doClose()
			self.write(output, self.CLOSED)
		else:
			self.write(output, self.ALREADY_CLOSED)
			
	def doClose(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_OPEN), False)
		self.closed = True
		
def _darkExamined(self, event):
	if not self.lit():
		self.write(event.output, self.DARKENED)
		
class Dark(Property):
	EVT_STATE_LIGHT = 'evtDarkLit'
	'''Fired when object's light state changes. Note that this event isn't fired
	if the object is lit by player's light source.'''
	
	LIT = 'darkLit'
	DARKENED = 'darkDarkened'
	HANDLE_DARK = "darkHandleDark"
	
	responses = {
		DARKENED : "It's dark in here.",
		HANDLE_DARK : "You can't do that in the dark."
	}
	
	def __init__(self, light=False, responses={}):
		Property.__init__(self, responses)
		self.light = light
		
	def initProp(self):
		self.owner.Normal.addEventListener(Normal.EVT_EXAMINED, (self, _darkExamined))
		
	def accessibleChildren(self):
		return self.lit()
		
	def doLight(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_LIGHT), True)
		self.light = True
			
	def doDarken(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_LIGHT), False)
		self.light = False
		
	def lit(self):
		for item in self.ownerGame().inventory:
			if item.hasProp('LightSource'):
				if self.owner.game.actor.canAccess(item):
					if not item.LightSource.inverse:
						return True
					else:
						return False
		
		return self.light
		
class LightSource(Property):
	def __init__(self, inverse=False, responses={}):
		Property.__init__(self, responses)
		self.inverse = inverse
			
class NPC(Property):
	EVT_ANSWERED = "evtNPCAnswered"
	'''Fired every time the NPC responds to the player's topic or question with something
	other than the default answer.'''
	EVT_CONVERSATION_STARTED = "evtNPCConversationStarted"
	'''Fired every time the player starts a conversation with NPC. Not fired when answering
	questions outside a conversation.'''
	EVT_CONVERSATION_ENDED = "evtNPCConversationEnded"
	'''Fired every time the player ends a conversation with NPC. Not fired when answering
	questions outside a conversation.'''
	
	CONVERSATION_STARTED = 'npcConversationStarted'
	CONVERSATION_ENDED = "npcConversationEnded"
	
	UNKNOWN_TOPIC = 'npcUnknownTopic'
	UNKNOWN_ORDER = 'npcUnknownOrder'
	UNKNOWN_QUESTION = 'npcUnknownQuestion'
	HELP = 'npcHelp'
	
	ANSWERED = "npcAnswered"
	
	ENDING = "end"
	
	responses = {
		CONVERSATION_STARTED:'"Yes?"',
		CONVERSATION_ENDED:'You end the conversation.',
		HELP:'(type topics you want to talk about - type "end" to end the conversation)',
		UNKNOWN_TOPIC : "\"I don't know anything about that.\"",
		UNKNOWN_ORDER : "\"I'm not going to do that.\"",
		UNKNOWN_QUESTION : "\"I don't know anything about that.\""
	}
	
	def __init__(self, topics={}, answers={}, orders={}, responses={}):
		Property.__init__(self, responses)
		self.topics = topics
		self.answers = answers
		self.orders = orders
		
	def handle(self, sentence, output):
		s = sentence[:3]
		
		if sentence == ('talk to', '*self'):
			self.initConversation()
			self.write(output, self.CONVERSATION_STARTED)
		elif s == ('talk to', '*self', 'about'):
			self.talkAbout(sentence[3:], output)
			self.write(output, self.UNKNOWN_TOPIC)
		elif s == ('ask', '*self', 'about'):
			self.answerQuestion(s, output)
			self.write(output, self.UNKNOWN_QUESTION)
		elif s == ('tell', '*self', 'to') or s == ('ask', '*self', 'to'):
			self.orderTo(sentence[3:], output)
			self.write(output, self.UNKNOWN_ORDER)
		
	def talkAbout(self, sentence, output):
		for topic in self.topics:
			if sentence == topic:
				self.answer(self.topics[topic], output)
				
		try:
			s = self.getScript()
			s = s.getChild('topics')
			for topic in s:
				if sentence == topic:
					output.write(s.getChild(topic).getValue(), obj=self.owner)
		except ScriptError:
			pass
				
				
	def answerQuestion(self, sentence, output):
		for answer in self.answers:
			if sentence == answer:
				self.answer(self.answers[answer], output)
				
		try:
			s = self.getScript()
			s = s.getChild('answers')
			for topic in s:
				if sentence == topic:
					output.write(s.getChild(topic).getValue(), obj = self.owner)
		except ScriptError:
			pass

	def orderTo(self, sentence, output):
		for answer in self.orders:
			if sentence == answer:
				self.answer(self.orders[answer], output)
		
		try:
			s = self.getScript()
			s = s.getChild('orders')
			for topic in s:
				if sentence == topic:
					output.write(s.getChild(topic).getValue(), obj = self.owenr)
		except ScriptError:
			pass
		
	def converseAbout(self, sentence, output):
		self.talkAbout(sentence, output)
		self.answerQuestion(sentence, output)
		output.write(self.responses[self.UNKNOWN_TOPIC], obj=self.owner)

	def answer(self, s, output):
		self.dispatchEvent(NPC.EVT_ANSWERED)
		output.write(s, obj=self.owner)
		
	def initConversation(self):
		self.dispatchEvent(NPC.EVT_CONVERSATION_STARTED)
		self.owner.game.setState(states.Talking(self.owner.game, self))
		
	def endConversation(self):
		self.dispatchEvent(NPC.EVT_CONVERSATION_ENDED)

class SimpleNPC(NPC):
	def answerQuestion(self, sentence, output):
		self.talkAbout(sentence, output)

def _seatMoved(self, event):
	if self.canStand:
		self.doStand()
		event.output.write(self.responses['itemMoved'], False, obj=self.owner)
	else:
		self.cantStand(event.output)


import items

class Seat(Property):
	EVT_SEATED = "evtSeatSeated"
	'''Fired every time the player sits on object.'''
	EVT_LAID = "evtSeatLaid"
	'''Fired every time the player lies down on object.'''
	EVT_STOOD = "evtSeatStood"
	'''Fired every time the player stands up from the object, regardless of whether
	he's sitting or lying.'''	
	EVT_CLIMBED = "evtClimbed"
	'''Fired every time player climbs on this object.'''
	
	SEATED = 'seatSeated'
	STOOD = 'seatStood'
	LAID = 'seatLaid'
	CANT_STAND = 'seatCantStand'
	
	responses = {
		SEATED: 'You sit down on [self.definite].',
		LAID: 'You lie down on [self.definite].',
		STOOD: 'You stand up.',
		'itemMoved': '(first standing up)',
		'climbed' : "You climb on [self.definite].",
		'getDown' : "You hop down from [self.definite].",
		'alreadyUp' : "You're already standing on [self.definite].",
		CANT_STAND: "You can't stand up!"
	}
	
	def __init__(self, seat=True, bed=False, platform=True, seated=False, canStand=True, responses={}):
		Property.__init__(self)
		self.seat = seat
		#: True if player can sit on this
		self.bed = bed
		#: True if player can lie on this
		self.canStand=canStand
		#: True if player can stand up once seated or lying on this
		self.platform = platform
		#: True if player can stand on this
		
		self.seated = False
		if seated:
			self.doSit()
		#: True if player is currently sitting on this
	
	def handle(self, sentence, output):
		if not self.seated:
			if self.seat:
				if sentence == ('sit',) or sentence == ('sit','*self'):
					self.sit(output)
					
			if self.bed:
				if sentence == ('lie down',) or sentence == ('lie down', '*self'):
					self.lie(output)
					
		if self.platform:
			if sentence == ("stand", 'on', '*self') or sentence == ('climb', 'on', '*self'):
				self.climb(output)
			elif sentence.actor.location == self.owner:
				if sentence == ("down",) or sentence == ("get", 'down') or sentence == ("get", 'down', 'from', '*self'):
					self.getDown(output)
					self.write(output, 'getDown')
			
		if self.seated:
			if self.seat or self.bed:
				if sentence == ('stand', 'up') or sentence == ('stand',):
					self.stand(output)
			
	def sit(self, output):
		self.doSit()
		self.write(output, self.SEATED)
		
	def climb(self, output):
		if output.actor.location != self.owner:
			self.doClimb()
			self.write(output, 'climbed')
		else:
			self.write(output, 'alreadyUp')
		
	def doClimb(self):
		self.dispatchEvent(self.EVT_CLIMBED)
		self.ownerGame().actor.intMove(self.owner)
		
	def getDown(self, output):
		output.actor.intMove(self.owner.owner)
		
	def lie(self, output):
		self.doLie()
		self.write(output, self.LAID)
		
	def doSit(self):
		self.dispatchEvent(self.EVT_SEATED)
		self.seated = True
		self.ownerGame().actor.addEventListener(items.Item.EVT_MOVED, (self,_seatMoved))		
		self.ownerGame().actor.addEventListener(items.Item.EVT_INT_MOVED, (self,_seatMoved))		
		
	def doLie(self):
		self.dispatchEvent(self.EVT_LAID)
		self.seated = True
		self.ownerGame().actor.addEventListener(items.Item.EVT_MOVED, (self,_seatMoved))
		self.ownerGame().actor.addEventListener(items.Item.EVT_INT_MOVED, (self,_seatMoved))		
		
	def doStand(self):
		self.dispatchEvent(self.EVT_STOOD)
		self.seated = False
		self.ownerGame().actor.removeEventListener(items.Item.EVT_MOVED, (self,_seatMoved))		
		self.ownerGame().actor.removeEventListener(items.Item.EVT_INT_MOVED, (self,_seatMoved))		

	def stand(self, output):
		if self.canStand:
			self.doStand()
			self.write(output, self.STOOD)
		else:
			self.cantStand(output)
		
	def cantStand(self, output):
		output.write(self.responses[self.CANT_STAND], obj=self.owner)

class Storage(Property):
	def describables(self, s):
		l = []
		for item in self.owner.inventory:
			try:
				if item.Mobile.autoDescribe:
					token = item.Normal.descToken()
					if token not in s:
						l.append(token)
			except AttributeError:
				pass
		
		return l

class Surface(Storage):
	PLACED = 'surfacePlaced'

	responses = {
		PLACED: "You finish placing it.",
		'surfaceInventory' : "There's %s on it."
	}

	def getDesc(self, type, desc):
		if type == 'long':
			l = self.describables(desc)

			s = utils.naturalJoin(l, ', ', ' and ')
			if s != '':
				return self.responses['surfaceInventory'] %s

	def handle(self, sentence, output):
		if sentence == ('put', '*noun', 'on', '*self'):
			item = sentence[1].item
			self.get(item, output)

	def get(self, target, output):
		if target.hasProp('Mobile'):
			target.move(self.owner)
			self.write(output, self.PLACED)

class Container(Storage):
	CLOSED_CONTAINER = 'containerClosedContainer'
	PLACED = "containerPlaced"
	NOT_CARRYING = "containerNotCarrying"
	
	responses = {
		CLOSED_CONTAINER : "You can't put things inside it.",
		PLACED : "You finish placing it.",
		'containerInventory' : "There's %s inside."
	}

	def getDesc(self, type, desc):
		if type == 'long' or type == 'Openable':
			l = self.describables(desc)
			s = utils.naturalJoin(l, ', ', ' and ')
			if s != '':
				return self.responses['containerInventory'] % s
		
	def handle(self, sentence, output):
		if sentence.actor.canAccess(self.owner):
			if sentence == ('put', '*noun', 'in', '*self'):
				if self.owner.accessibleChildren() == False:
					self.write(output, self.CLOSED_CONTAINER)
			
				item = sentence[1].item
				item.move(self.owner)
				self.write(output, self.PLACED)
				
class Room(Container):
	responses = {
		Container.CLOSED_CONTAINER : "You can't put things inside it.",
		Container.PLACED : "You finish placing it.",
		'containerInventory' : "You can also see %s here."
	}
	
class Appliance(Property):
	EVT_STATE_ON = 'evtStateOn'
	
	responses = {
		'turnedOff' : "It's turned off.",
		'turnedOn' : "It's turned on.",
		'turnOn' : 'You turn on [self.definite].',
		'alreadyTurnedOn' : "It's already turned on.",
		'turnOff' : 'You turn on [self.definite].',
		'alreadyTurnedOff' : "It's already turned off."
	}
	
	def __init__(self, on=False, responses={}):
		Property.__init__(self,responses)
		self.on = on
	
	def getDesc(self, type, desc):
		if type == 'long':
			if self.on:
				return self.responses['turnedOn']
			else:
				return self.responses['turnedOff']
				
	def handle(self, sentence, output):
		s = sentence
		if s == ('turn', '*self', 'on') or s == ('turn on', '*self',):
			self.turnOn(output)
		elif s == ('turn', '*self', 'off') or s == ('turn off', '*self',):
			self.turnOff(output)
				
	def turnOn(self, output):
		if not self.on:
			self.doTurnOn()
			self.write(output, 'turnOn')
		else:
			self.write(output, 'alreadyTurnedOn')
			
	def doTurnOn(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_ON), True)
		self.dispatchEvent(self.EVT_TURNED_ON)
		self.on = True
			
	def turnOff(self, output):
		if self.on:
			self.doTurnOff()
			self.write(output, 'turnOff')
			
	def doTurnOff(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_ON), False)
		self.on = False
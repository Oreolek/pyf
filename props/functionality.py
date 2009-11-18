'''Defines properties that define a use for the item, such as electronic appliances
and furniture.'''

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
from .. props import Property, SwitchEvent

def _seatMoved(self, event):
	if self.canStand:
		self.doStand()
		event.output.write(self.responses['itemMoved'], False)
	else:
		self.cantStand(event.output)

class Seat(Property):
	"""Defines item as something that can be sat, lain or stood on."""
	EVT_SEATED = "evtSeated"
	'''Fired before actor sits on object.'''
	EVT_LAIN = "evtLain"
	'''Fired before actor lies down on object.'''
	EVT_STOOD = "evtStood"
	'''Fired before actor stands up from the object, regardless of whether
	he's sitting or lying.'''	
	EVT_CLIMBED = "evtClimbed"
	'''Fired before actor climbs on object.'''
	
	SEATED = 'seatSeated'
	STOOD = 'seatStood'
	LAIN = 'seatLain'
	CANT_STAND = 'seatCantStand'
	CLIMBED = "climbed"
	'''Shown when player stands on item.'''
	
	responses = {
		SEATED: 'You sit down on [self.definite].',
		LAIN: 'You lie down on [self.definite].',
		STOOD: 'You stand up.',
		'itemMoved': '(first standing up)',
		CLIMBED : "You climb on [self.definite].",
		'getDown' : "You hop down from [self.definite].",
		'alreadyUp' : "You're already standing on [self.definite].",
		CANT_STAND: "You can't stand up!"
	}
	
	def __init__(self, seat=True, bed=False, platform=True, seated=False, canStand=True):
		Property.__init__(self)
		self.seat = seat
		"""True if player can sit on this"""
		self.bed = bed
		"""True if player can stand up once seated or lying on this"""
		self.canStand=canStand
		"""True if player can stand on this"""
		self.platform = platform
		
		"""True if player is currently sitting on this"""
		self.seated = False
		if seated:
			self.doSit()
	
	def handle(self, sentence, output):
		if not self.seated:
			if self.seat:
				if sentence == ('sit',) or sentence == ('sit','*self'):
					self.sit(output)
					
			if self.bed:
				if sentence == ('lie down',) or sentence == ('lie down', '*self'):
					self.lie(output)
					
		if self.platform:
			if sentence == ('climb', '*self'):
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
		self.ownerGame.actor.intMove(self.owner)
		
	def getDown(self, output):
		output.actor.intMove(self.owner.owner)
		
	def lie(self, output):
		self.doLie()
		self.write(output, self.LAIN)
		
	def doSit(self):
		self.dispatchEvent(self.EVT_SEATED)
		self.seated = True
		actor = self.ownerGame.actor
		actor.addEventListener(actor.EVT_INT_MOVED, (self, _seatMoved))		
		actor.addEventListener(self.owner.EVT_INT_MOVED, (self, _seatMoved))		
		
	def doLie(self):
		self.dispatchEvent(self.EVT_LAIN)
		self.seated = True
		actor = self.ownerGame.actor
		actor.addEventListener(actor.EVT_INT_MOVED, (self,_seatMoved))		
		actor.addEventListener(self.owner.EVT_INT_MOVED, (self, _seatMoved))		
		
	def doStand(self):
		self.dispatchEvent(self.EVT_STOOD)
		self.seated = False
		actor = self.ownerGame.actor
		actor.removeEventListener(actor.EVT_INT_MOVED, (self,_seatMoved))		
		actor.removeEventListener(self.owner.EVT_INT_MOVED, (self, _seatMoved))

	def stand(self, output):
		if self.canStand:
			self.doStand()
			self.write(output, self.STOOD)
		else:
			self.cantStand(output)
		
	def cantStand(self, output):
		output.write(self.responses[self.CANT_STAND])


		
class Wearable(Property):
	"""Defines item as something that can be worn."""
	EVT_STATE_WORN = "evtStateWorn"
	'''Fired every time the object's worn state is changed'.'''
	
	STRIPPED = 'wearableStripped'
	WORN = 'wearableWorn'
	ALREADY_STRIPPED = 'wearableAlreadyStripped'
	ALREADY_WORN = 'wearableAlreadyWorn'
	STRIPPED_INLINE = 'wearableStrippedInline'
	NO_WEAR = 'noWear'
	INV_WORN = 'invWorn'
	
	responses = {
		STRIPPED: "You finish taking [self.definite] off.",
		ALREADY_STRIPPED : "You're not wearing [self.definite].",
		WORN: "You finish putting [self.definite] on.",
		ALREADY_WORN: "You're already wearing [self.definite].",
		STRIPPED_INLINE: '(first taking [self.definite] off)',
		INV_WORN : "(worn)",
		'wearableCurrentlyWearing' : "You're currently wearing [self.pronoun]."
		
	}
	
	def __init__(self, worn=False):
		Property.__init__(self)
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
		
	def init(self):
		self.owner.addEventListener(self.owner.EVT_MOVED, (self, _wearableMoved))
		
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

def _wearableMoved(self, event):
	if event.output != None:
		if self.worn:
			self.doStrip()
			self.write(event.output, self.STRIPPED_INLINE, False)



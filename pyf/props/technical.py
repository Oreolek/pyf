'''Classes for technical properties of items. Includes buttons, switches, and electronics.'''

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

class Appliance(Property):
	'''Implements funcionality typical for electronic devices. Allows turning item on and
	off.
	
	turn *self on	:	/
	turn on *self	:	turn it on
		
	turn *self off	:	/
	turn off *self	:	turn it off'''
		
	EVT_STATE_ON = 'evtStateOn'
	'''Fired when object is turned on or off.'''
	
	TURNED_ON = "turnedOn"
	"""Appended to object's long description when it's turned on."""
	TURNED_OFF = "turnedOff"
	"""Appended to object's long description when it's turned off."""
	TURN_ON = "turnOn"
	"""Printed when player turns object on."""
	ALREADY_ON = "alreadyTurnedOn"
	"""Printed when item is already turned on."""
	TURN_OFF = "turnOff"
	"""Printed when player turns object off."""
	ALREADY_OFF = "alreadyTurnedOff"
	"""Printed when item is already turned off."""
	
	responses = {
		'turnedOff' : "It's turned off.",
		'turnedOn' : "It's turned on.",
		'turnOn' : 'You turn on [self.definite].',
		'alreadyTurnedOn' : "It's already turned on.",
		'turnOff' : 'You turn off [self.definite].', 
		'alreadyTurnedOff' : "It's already turned off."
	}
	def __init__(self, on=False):
		Property.__init__(self)
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
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_ON, True))
		self.on = True
			
	def turnOff(self, output):
		if self.on:
			self.doTurnOff()
			self.write(output, 'turnOff')
			
	def doTurnOff(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_ON, False))
		self.on = False
		
class Button(Property):
	'''A simple button that retains no information about whether it's been pressed.
	
		push *self /
		press *self	:	fire EVT_PRESSED'''
	EVT_PRESSED = 'evtPressed'
	'''Fired before button has been pressed.'''
	
	PRESSED = 'pressed'
	
	responses = {
		PRESSED : '[self.definite] clicks. Nothing seems to have happened.'
	}
	
	def handle(self, sentence, output):
		if sentence[0] in ('push', 'press'):
			if sentence[1:] == ('*self',):
				self.dspatchEvent(EVT_PRESSED, output)
				self.write(output, self.EVT_PRESSED)
				
class Lever(Property):
	"""A simple lever.
	
	push *self	:	set pushed as True
	pull *self	:	set pushed as False
	turn *self	:	switch it"""
	
	EVT_STATE_TURNED = 'evtStateSwitched'
	'''Fired before the lever is moved. '''
	
	PUSHED = 'pushed'
	'''Default msg after player has pushed the lever.'''
	PULLED = 'pulled'
	'''Default msg after player has pulled the lever.'''
	ALREADY_PUSHED = 'alreadyPushed'
	'''Default msg after player tries pushing a lever that's already pushed.'''
	ALREADY_PULLED = 'alreadyPulled'
	'''Default msg after player tries pulling a lever that's already pulled.'''
	CANT_TURN = 'cantTurn'
	'''Default msg after player tries turning a lever that can't be turned.'''
	
	responses = {
		PUSHED : "You push the lever.",
		PULLED : "You pull the lever.",
		ALREADY_PUSHED : "You can't push it any farther.",
		ALREADY_PULLED : "You can't pull it any farther.",
		CANT_TURN : "You'll have to specify which direction to turn it in.",
	}
	
	def __init__(self, pushed=True, turnable=True):
		self.pushed = pushed
		'''Its current position.'''
		self.turnable = turnable
		'''True if player can use 'turn *self' to switch its state.'''
		
	def handle(self, sentence, output):
		if sentence == ('push', '*self'):
			if self.pushed == True:
				self.write(output, self.ALREADY_PUSHED)
			else:
				self.switch(output)
				self.write(output, self.PUSHED)
		elif sentence == ('pull', '*self'):
			if self.pushed == False:
				self.write(output, self.ALREADY_PULLED)
			else:
				self.switch(output)
				self.write(output, self.PULLED)
				
		elif sentence == ('turn', '*self'):
			if self.turnable:
				self.switch(output)
				if self.pushed:
					self.write(output, self.PULLED)
				else:
					self.write(output, self.PUSHED)
			else:
				self.write(output, self.CANT_TURN)
			
	def switch(self, output):
		s = self.pushed == False
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_TURNED, s), output)
		self.pushed = s
		
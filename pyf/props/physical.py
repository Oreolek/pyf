'''Defines props that affect the physical properties of items.'''

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
from containers import Container
from general import Mobile

class Liquid(Property):
	'''Define item as liquid.'''
	
	EVT_POURED = 'evtPoured'
	'''Fired before liquid is poured somewhere.'''
	
	name = "Mobile"
	'''Replace default Mobile.'''
	
	POURED = 'poured'
	ALREADY_POURED = 'alreadyPoured'
	NOT_CONTAINER = "notContainer"
	NOT_LIQUID_CONTAINER = "notLiquidContainer"
	
	responses = {
		POURED : "You pour [self.definite] in [nouns[1].definite].",
		ALREADY_POURED : "[self.definite] is already in [nouns[1].definite].",
		NOT_CONTAINER : "You can't put things in [nouns[1].definite].",
		NOT_LIQUID_CONTAINER : "[nouns[1].definite] isn't something that can hold liquid.",
	
	}
	
	def __init__(self, autoDescribe=True):
		self.autoDescribe = autoDescribe
	
	def doPour(self, item):
		self.dispatchEvent(self.EVT_POURED)
		self.owner.move(item)
	
	def handle(self, sentence, output):
		if sentence == ('pour', '*self', 'in', '*noun'):
			item = sentence[-1].item
			if Container in item.props:
				if item.Container.canHoldLiquid:
					if item != self.owner.owner:
						self.doPour(item)
						self.write(output, self.POURED)
					else:
						self.write(output, self.ALREADY_POURED)
				else:
					self.write(output, self.NOT_LIQUID_CONTAINER)
			else:
				self.write(output, self.NOT_CONTAINER)
	
class Hot(Property):
	'''Define item as too hot to touch.'''
	EVT_STATE_HOT = 'evtStateHot'
	'''Fired before property's hotness state is changed.'''
	
	TOO_HOT = "tooHot"
	
	responses = {
		TOO_HOT : "[self.definite] is too hot to touch!"
	}
	
	def __init__(self, hot=True):
		Property.__init__(self)
		
		self.hot = hot
		'''True if object is too hot to touch directly.'''
	
	def handle(self, sentence, output):
		if output == ('*touch', '*self'):
			self.write(output, self.TOO_HOT)
			
	def doCool(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_HOT, False))
		self.hot = False
		
	def doCool(self):
		self.dispatchEvent(SwitchEvent(self.EVT_STATE_HOT, True))
		self.hot = True
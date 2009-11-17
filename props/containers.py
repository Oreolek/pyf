"""Defines properties that can be used to store items in another item."""

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
from general import Mobile
from .. import utils

class Storage(Property):
	"""Superclass for properties that are used to contain items."""
	INVENTORY = 'inventory'
	
	def describables(self, s):
		l = []
		for item in self.owner.inventory:
			if Mobile in item.props:
				if item.Mobile.autoDescribe:
					token = item.Normal.descToken()
					#if token not in s:
					l.append(token)
		
		return l
		
	def getDesc(self, type, desc):
		if type == 'long':
			l = self.describables(desc)

			s = utils.naturalJoin(l, ', ', ' and ')
			if s != '':
				return self.responses[self.INVENTORY] %s

class Surface(Storage):
	"""Define item as something that can contain other items on it."""
	PLACED = 'surfacePlaced'

	responses = {
		PLACED: "You finish placing [self.pronoun].",
		Storage.INVENTORY : "There's %s on [self.pronoun]."
	}

	def handle(self, sentence, output):
		if sentence == ('put', '*noun', 'on', '*self'):
			item = sentence[1].item
			self.get(item, output)

	def get(self, target, output):
		if Mobile in target.props:
			target.move(self.owner)
			self.write(output, self.PLACED)

class Container(Storage):
	"""Define item as something that can contain other items inside it."""

	CLOSED_CONTAINER = 'closedContainer'
	PLACED = "placed"
	NOT_CARRYING = "notCarrying"
	EMPTIED = "emptied"
	
	responses = {
		CLOSED_CONTAINER : "You can't put things inside [nouns[1].definite].",
		PLACED : "You place [self.definite] inside [nouns[1].definite].",
		Storage.INVENTORY : "There's %s inside.",
		EMPTIED : "You empty the contents of [self.definite] on the ground."
	}
	
	def __init__(self, canHoldLiquid=True):
		Storage.__init__(self)
		self.canHoldLiquid = canHoldLiquid
		'''True if container can hold liquid.'''

	def getDesc(self, type, desc):
		if type == 'long' or type == 'Openable':
			l = self.describables(desc)
			s = utils.naturalJoin(l, ', ', ' and ')
			if s != '':
				return self.responses[self.INVENTORY] % s
		
	def handle(self, sentence, output):
			if sentence == ('put', '*noun', 'in', '*self'):
				if self.owner.accessibleChildren() == False:
					self.write(output, self.CLOSED_CONTAINER)
			
				item = sentence[1].item
				item.move(self.owner)
				self.write(output, self.PLACED)
			elif sentence == ("empty", '*self'):
				for item in self.owner.inventory:
					if Mobile in self.owner.inventory:
						item.Mobile.doDrop()
				self.write(output, self.EMPTIED)
						
				
class Room(Container):
	"""Automatically append descriptions of all moved objects to room description."""
	responses = {
		Container.CLOSED_CONTAINER : "You can't put things inside [self.definite].",
		Container.PLACED : "You finish placing [self.definite].",
		Container.INVENTORY : "You can also see %s here."
	}
	


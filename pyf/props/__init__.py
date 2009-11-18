'''Properties are used to append re-usable functionality to items.'''

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

from pyf import handler
import copy
from .. errors import PropError, MoveError
# epydoc doesn't allow importing *

class SwitchEvent(handler.HandlerEvent):
	'''Used for events that are fired by a simple switch in the object's state.'''
	def __init__(self, type, value):
		handler.HandlerEvent.__init__(self, type, None)
		self.value = value
		'''value that the switch is being changed to'''

class PropertyMeta(handler.HandlerMeta):
	@property
	def name(cls):
		return getattr(cls, '_name', cls.__name__)
		
	@name.setter
	def name(cls, value):
		cls._name = value

class Property(handler.Handler):
	'''Superclass for all properties.'''
	__metaclass__ = PropertyMeta
	
	def __eq__(self, other):
		if type(self) == other:
			return True
		elif type(other) == PropertyMeta:
			return self.name == other.name
		else:
			return False
			
	@property
	def name(self):
		return self.__class__.name
			
	def move(self, dest):
		'''Add prop to dest property list. If dest already has an property with self.name,
		raise MoveError.
		
		@type	dest:	Item
		'''
		if type(self) in dest.props:
			raise MoveError("%s already has property %s" % (str(dest), self.name))
		else:
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

	def getDesc(self, type, desc):
		return None
		
	@property
	def ownerGame(self):
		'''Returns the game of the Item this property belongs to.'''
		if self.owner == None:
			raise PropError("Property %s's owner is set to None" % self.__class__.__name__)
		return self.owner.game
		
	def handleScript(self, sentence, output):
		pass

		
from characters import *
from containers import *
from functionality import *
from general import *
from physical import *
from technical import *
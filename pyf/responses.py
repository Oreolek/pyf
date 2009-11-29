'''Classes for standard handler responses.'''

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

import handler

class Responses:
	'''Container class for handler responses.'''
	
	def __init__(self, parent, dict):
		self.parent = parent
		self.dict = dict
		
	@property
	def ownerGame(self):
		return self.parent.ownerGame
		
	def XMLSetup(self, node):
		for n in node.children:
			if n.node.nodeName == 'response':
				if n.node.hasAttribute('id'):
					s = n.getValue()
					self[n.node.getAttribute('id')] = s
	
	def __getitem__(self, name):
		'''Try retrieving value from owner handler's ScriptNode before looking up the dict.'''
		return self.dict[name]
			
	def __setitem__(self, name, value):
		handler.log(self, 'dict')
		self.dict[name] = value
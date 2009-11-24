'''Inventory container class.'''

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

from errors import *

class Inventory:
	'''Item container class. Main function is to allow iterating through inventory
	while skipping any unavailable items.'''
	def __init__(self):
		'''Item this inventory belongs to'''
		self.list = []
		'''list of items in inventory'''
		
	def __iter__(self):
		'''Iterate through item list skipping unavailable items.'''
		for item in self.list:
			if item.available:
				yield item
			
	def __getitem__(self, i):
		'''Get item at index i.'''
		return self.list[i]
		
	def __len__(self):
		'''Get inventory length.'''
		return len(self.list)
			
	def remove(self, item):
		'''Remove item from item list.'''
		self.list.remove(item)
		
	def append(self, item):
		'''Add item to inventory list. Raises InventoryError if item is already in 
		list.'''
		if item in self.list:
			raise InventoryError("Item %s already found in inventory." % str(item.name))
		self.list.append(item)

	def __contains__(self, other):
		'''Returns other in itemList.'''
		return other in self.list
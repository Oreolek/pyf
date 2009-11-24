'''Classes for distributing and opening PyF formatted zip-files.'''

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

import os, os.path
from zipfile import ZipFile

class Importer:
	'''Importer class is used for running PyF formatted zip-files.'''
	
	def __init__(self, file):
		self.file = file
		f = self.file.open('__init__.py')
		self.content = f.read()
		
		self.content = self.content.replace('\r\n', '\n')
        
		f.close()
		
		self.locals = {'open': self.open, 'file': self.open}
		self.globals = {'open': self.open, 'file': self.open}
		
		exec(self.content, self.locals)
		
	def game(self):
		"""Return current game object, imported from the __init__.py source file."""
		return self.locals['game']
		
	def open(self, *args, **kwargs):
		'''Game uses this open function instead of the default Python one for opening
		files in the current zip archive. '''
		return self.file.open(*args, **kwargs)
		
class Packer:
	'''Packer class is used for creating PyF formatted zip-files.'''
	
	@classmethod
	def pack(cls, path, name="game.pyf"):
		"""Create new game file.
		
		@param	path: str
		@param	name: str - Name of the file to create. """
		
		z = ZipFile(os.path.join(path, name), 'w')
		for f in os.listdir(path):
			if f != name:
				if os.path.isfile(os.path.join(path, f)):
					z.write(os.path.join(path, f), f)
		z.close()
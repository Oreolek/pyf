"""Basic classes for writing output."""

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

import types
from errors import *

class Output:
	'''Class for writing output responding to user's input. This object is taken through
	the handling process by the state object.'''
	
	i = None
	
	def __init__(self):
		self.open()
		
		self.lines = []
		self.canClose = True
		self.target = None
		
	def write(self, s, close=True, obj=None, separators=('[',']')):
		'''Write new output.
		
		s : string / function / list - Function is called without arguments
		and return value is written as output. List extends lines.
		close : Bool - Close the output and stop processing input.
		obj : Item - Set to process output between separators as code. Code is ran as a
		lambda function. obj is set as self in the scope of the function.
		separators : tuple - 2 item tuple containing the separators to when parsing output
		for code. Default value is ("[", "]").'''
		if self.closed:
			self.done()
		else:
			if type(s) == types.FunctionType:
				s = s()
			if type(s) == str or type(s) == unicode:
				s = [s]
			
			for line in s:
				if obj != None:
					line = self.eval(line, obj, separators)
					
				line = self.cleanOutput(line)
				line = line.strip()
				self.lines.append(line)
			
		if close:
			self.close()
			
	def eval(self, s, obj, separators):
		'''Run through string s evaluating any code contained in separators.
		
		s : str
		obj : Item
		separators : tuple'''
		out = ''
		codeBuffer = ''
		
		count = 0
		for char in s:
			if char == separators[0]:
				count += 1

			elif char == separators[1]:
				count -= 1
				if count == 0:
					out += eval(codeBuffer, {'self': obj})
					codeBuffer = ''

			elif count > 0:
				codeBuffer+=char

			elif count < 0:
				raise OutputError("Separator imbalance in code '%s'" % s)

			else:
				out+=char

		return out
			
	def __str__(self):
		s = '\n'.join(self.lines)
		s = s.replace("\t",'')
		while '  ' in s:
			s = s.replace('  ', ' ')
		return s
		
	def close(self):
		'''Close output and raise OutputClosed. If self.canClose = False raise 
		OutputError.'''
		Output.i = None
		
		if self.canClose:
			self.closed = True
			raise OutputClosed("Output closed")
		else:
			raise OutputError("Can't close output while in the timed event handling phase.")
			
	def open(self):
		self.closed = False
		Output.i = self
		
	def done(self):
		raise OutputClosed("Can't write to closed output")
		
	@classmethod
	def cleanOutput(cls, s):
		'''Clean extra whitespace from string.
		
		s : str'''
		try:
			s = s()
		except TypeError:
			pass
		s = s.replace("\t", ' ')
		s = s.replace("\n", ' ')
		while '  ' in s:
			s = s.replace('  ', ' ')
		try:
			s = s[0].upper() + s[1:]
		except IndexError:
			pass
		return s
		
	@classmethod
	def inst(cls):
		'''Return current class instance.'''
		if cls.i == None:
			raise OutputError("Output unavailable")
		else:
			return cls.i
		
def cleanInput(s):
	pass
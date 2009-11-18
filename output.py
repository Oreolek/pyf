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

import types, utils
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
		
		self.sentence = None
		'''Input associated with this output.'''
		
	def write(self, s, close=True, separators=('[',']'), obj=None):
		'''Write lines into output.
		
		@type	s:	string / function / list 
		@param	s:	Function is called without arguments and return value is written as 
					output. List extends lines.
			
		@type	close:	Bool 
		@param	close:	Close the output and stop processing input.
		
		@type	obj:	Item 
		@param	obj:	Set to process output between separators as code. Code is ran as a
						lambda function. obj is set as self in the scope of the function.
						separators : tuple - 2 item tuple containing the separators to when
						parsing output for code. Default value is ("[", "]").'''
						
		if self.closed:
			self.done()
		else:
			if type(s) == types.FunctionType:
				s = s()
			if type(s) == str or type(s) == unicode:
				s = [s]
			
			for line in s:
				line = self.eval(line, separators, obj)
					
				line = self.cleanOutput(line)
				line = line.strip()
				self.lines.append(line)
			
		if close:
			self.close()
			
	def eval(self, s, separators, obj=None):
		'''Run through string s evaluating any code contained in separators.
		
		@type	s:			str
		@param	s:			String to search. Text between separators is evaluated.
		
		@type	obj:		Item / None
		@param	obj:		Item to set as self for code between separators.
		
		@type	separators:	tuple
		@param	separators:	2-item tuple containing separators to use for separating
		 					code from text.
		
		@rtype:				str
		@return:			str with code between separators evaluated.'''
		
		'''TODO:			Code should retain the context of the module item was
							defined in.'''
							
		nouns = None
		items = None
		verbs = None
		sentence = None
		actor = None
		
		if not self.sentence is None:
			nouns = self.sentence.nouns
			verbs = self.sentence.verbs
			items = [word.item for word in self.sentence.nouns]
			sentence = self.sentence
			actor = self.sentence.actor
			if not obj:
				try:
					obj = items[0]
				except IndexError:
					obj = None
			
		out = ''
		codeBuffer = ''
		
		count = 0
		for char in s:
			if char == separators[0]:
				count += 1
				if count == 1:
					continue

			elif char == separators[1]:
				count -= 1
				if count == 0:
					try:
						out += eval(codeBuffer, {'self': obj, 'nouns':nouns, 'items':items, 'verbs':verbs, 'sentence':sentence, 'actor':actor, 'utils':utils})
					except Exception, e:
						raise InlineCodeError('Error in inline code: [%s] in \n %s \n' % (codeBuffer, s) + str(e))
					codeBuffer = ''
					continue
				

			if count > 0:
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
			raise OutputClosed()
		else:
			raise OutputError("Can't close output while in the timed event handling phase.")
			
	def open(self):
		self.closed = False
		Output.i = self
		
	def done(self):
		raise OutputClosed()
		
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
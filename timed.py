"""Contains various classes useful for creating timed events."""

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

from xml.dom import minidom
import handler, script
from errors import *

class TimedEvent(object):
	def __init__(self, function, i):
		self.i = i
		'''Turns after which function should be executed. 0 means function is executed
		immediately.'''
		
		self.function = function
		'''Function to execute after timer reaches i.'''
		self.count = 0
		self.done = False
		
	def handle(self, sentence, output):
		self.count += 1
		if self.count > self.i:
			try:
				self.function(sentence, output)
			except OutputClosed:
				pass
			self.done = True

class Scene(object):
	scenes = {}
	def __init__(self, name):
		self.l = []
		
	def handle(self, sentence, output):
		current = self.l.pop()
		handled = False
		
		try:
			current.handlers.handle(sentence, output)
			if current == Pause:
				self.l.append(current)

		except OutputClosed:
			handled = True
		
		if current.active:
			output.write(str(current), False)
		if handled:
			raise OutputClosed()
	
	@property
	def done(self):
		if len(self.l):
			return False
		else:
			return True
			
	def XMLSetup(self, node):
		if node.node.hasAttribute('name'):
			self.scenes[node.node.getAttribute('name')] = self
		for child in node.children:
			if child.node.tagName == 'line':
				l = Line()
			elif child.node.tagName == 'pause':
				l = Pause()
			else:
				continue
				
			l.XMLSetup(child)
			self.l.append(l)
		self.l.reverse()

	def XMLWrapup(self, node):
		pass
			
class Line(object):
	def __init__(self):
		self.handlers = handler.HandlerAccess(self)
		self.active = True
		
	def XMLSetup(self, node):
		self.s = node.getValue()
		current = node.node.previousSibling
		while current != None:
			if current.__class__ != minidom.Text:
				if current.tagName != 'response':
					break

				self.handlers[current.getAttribute('sentence')] = script.XMLScriptNode(current, node.dict).getValue()
			current = current.previousSibling
		
	def __str__(self):
		return self.s
		
	def __eq__(self, other):
		if type(self) == other:
			return True
		else:
			return id(self) == id(other)
		
class Pause(Line):
	def __str__(self):
		self.active = False
		return Line.__str__(self)

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

class Scene(object):
	def __init__(self):
		self.l = []
		
	def __call__(self, sentence, output):
		current = self.l.pop()

		try:
			current.handlers.handle(sentence, output)
			if current == Pause:
				self.l.append(current)
		except OutputError:
			pass
		
		if current.active:
			output.write(str(current), False)
		
		if len(self.l) == 0:
			return False
		else:
			return True
			
	def XMLSetup(self, node):
		for child in node.children:
			if child.node.tagName == 'line':
				l = Line()
			elif child.node.tagName == 'pause':
				l = Pause()
				child = child.getChild('line')
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
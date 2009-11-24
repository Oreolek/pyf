'''Classes for reading script files.'''

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
from errors import *

class XMLScriptNode:
	elementClass = minidom.Element
	safe = {}
	
	def __init__(self, node, dict):
		self.node = node
		self.dict = dict
		self.children = []
		self.node.normalize()
		for node in self.node.childNodes:
			if node.__class__ == self.elementClass:
				self.children.append(XMLScriptNode(node, dict))
		
	def getChild(self, name):
		for node in self.children:
			if node.node.tagName == name:
				return node
		raise ScriptChildError("No tags with name %s found in %s" % (name, self.node))
		
	def createChildren(self, root):
		l = []
		for child in self.children:
			o = child.create()
			if o:
				l.append(o)
				l.extend(child.createChildren(o))
				if root:
					try:
						o.move(root)
					except MoveError:
						o = root.getProp(o.name)
						o.XMLSetup(child)
				o.XMLWrapup(child)

		return l

	def create(self):
		try:
			cls = self.getClass()
		except ScriptClassError:
			return
			
		if hasattr(cls, '__call__'):
			o = cls()
		else:
			cls.XMLSetup(self)
			return cls

		if self.node.hasAttribute('as'):
			self.safe[self.node.getAttribute('as')] = o
			
		if hasattr(o, 'XMLSetup'):
			o.XMLSetup(self)

		return o
		
	def elementName(self):
		return self.node.tagName.rsplit(':')[-1]
			
	def getModuleDict(self):
		dict = self.dict
		if self.node.namespaceURI:
			string = self.node.tagName.rsplit(':',1)[1]
			
			f = __import__(self.node.namespaceURI)
			for s in self.node.namespaceURI.split('.')[1:]:
				dict = getattr(f, s).__dict__
		
		return dict
			
	def getValue(self):
		s = ''
		for child in self.node.childNodes:
			try:
				s += child.nodeValue.strip()
			except AttributeError:
				f = XMLScriptNode(child, self.dict).getClass()
				return f

		if self.node.getAttribute('type') != '':
			return eval('%s(%s)' % (self.node.getAttribute('type'), s))
		else:
			return s
			
	def getClass(self):
		dict = self.getModuleDict()
		name = self.elementName()
		if name not in dict:
			raise ScriptClassError("Name %s not found in module dict." % name)
		else:
			return dict[name]
			
class XMLScript(XMLScriptNode):
	def __init__(self, s, dict):
		self.doc = minidom.parseString(s)
		self.doc.normalize()
		XMLScriptNode.__init__(self, self.doc.documentElement, dict)
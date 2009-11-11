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
	safe = {}
	
	def __init__(self, node, dict):
		self.node = node
		self.dict = dict
		self.node.normalize()
		self.children = []
		for node in self.node.childNodes:
			try:
				self.children.append(XMLScriptNode(node, dict))
			except TypeError:
				pass
		
	def getChild(self, name):
		e = self.node.getElementsByTagName(name)
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
					o.move(root)
				o.XMLWrapup(child)

		return l

	def create(self):
		node = self.node
		try:
			cls = self.getClass()
			o = cls()
			if self.node.hasAttribute('as'):
				self.safe[self.node.getAttribute('as')] = o
			try:
				o.XMLSetup(self)
			except AttributeError:
				pass
			return o
		except ScriptClassError:
			pass
			
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
			if child.__class__ != minidom.Text:
				f = XMLScriptNode(child, self.dict).getClass()
				return f
			s += child.nodeValue.strip()

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
		
	def getNode(self, address):
		raise ScriptError
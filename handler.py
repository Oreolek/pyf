'''Basic handler classes.'''

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

import new, responses, copy
from errors import *

class HandlerMeta(type):
	def __call__(cls, *args, **kwargs):
		f = type.__call__(cls, *args, **kwargs)
		f.handlers = HandlerAccess(f)
		f.listeners = f.listeners.copy()
		f.responses = responses.Responses(f, f.responses)
		f.init()
		return f
		
	def __new__(cls, *args, **kwargs):
		o = type.__new__(cls, *args, **kwargs)
		o.responses = o.responses.copy()
		o.listeners = {}
		o.inst = None
		return o

class Handler(object):
	'''Base class for any object that needs to handle sentences.'''
	
	__metaclass__ = HandlerMeta
	responses = {}
		
	def __init__(self):
		#: HandlerAccess - Dict like item for default sentence handlers.
		self.owner = getattr(self, 'owner', None)
		
		self.responses = self.responses.copy()
		
	def XMLSetup(self, node):
		for child in node.children:
			if child.node.tagName == 'attr':
				self.assignFromXMLNode(child)
			elif child.node.tagName == 'event':
				self.addEventListener(child.node.getAttribute('id'), child.getValue())
		self.handlers.XMLSetup(node)
		self.responses.XMLSetup(node)
		
		
	def assignFromXMLNode(self, node):
		for n in node.children:
			if hasattr(self, n.node.nodeName):
				try:
					self.__dict__[n.node.nodeName] = n.getValue()
				except ScriptClassError:
					pass
			else:
				raise ScriptError("%s has no attribute %s" % (self, n.node.nodeName))
					
	def XMLWrapup(self, node):
		pass
		
	def write(self, output, name, close=True, obj = None):
		'''Convenience function - write self.responses[name] to output with
		obj set as self.owner.'''
		output.write(self.responses[name], close=close, obj=obj)

	def init(self):
		"""Set up any user defined variables for item. Default implementation does nothing."""
		pass
		
	def initFromScriptNode(self, node, dict):
		pass
		
	@property
	def ownerGame(self):
		'''return : Game'''
		try:
			if self.game is None:
				raise AttributeError("%s has no game" % self)
			return self.game
		except AttributeError:
			raise GameError("Object %s hasn't been added to a game yet." % str(self))
	
	def dispatchEvent(self, event, output=None):
		'''Dispatch an event in to the event flow.
		
		@type	event:	str / HandlerEvent
		@param	event:	str - create new HandlerEvent with type event
			HandlerEvent - passed to handlers as is
			
		@type	target:	Handler
		@param	target: set as event target'''
		
		if isinstance(event, str):
			type = event
			event = HandlerEvent(event, None)
		else:
			type = event.type

		event.target = self
		
		if event.output is None:
			try:
				event.output = self.ownerGame.actor.output
			except GameError:
				pass
		
		try:
			for f in self.listeners[type]:
				if f.__class__ in (tuple, list):
					f[-1](*f[:-1] + (event,))
				else:
					if event.output != None:
						event.output.write(f)
		except KeyError:
			pass
			
	@classmethod
	def addClassEventListener(cls, type, function):
		if type not in cls.listeners:
			cls.listeners[type] = []
		cls.listeners[type].append(function)

	def addEventListener(self, type, handler):
		'''Add event listener.
		
		type : str - The event type to listen to.
		handler : tuple - 2-item tuple where the first item is self object for the
		function and second is a function or a callable object.'''
		validateHandlerFunction(handler[1])
			
		try:
			l = self.listeners[type]
		except KeyError:
			self.listeners[type] = []
			l = self.listeners[type]
			
		l.append(handler)
		
	def removeEventListener(self, type, function):
		'''Remove event listener.
		
		type : str
		function : tuple'''
		self.listeners[type].remove(function)
	
	def intHandle(self, sentence, output):
		'''Default sentence handling process. Should be called only from State.handle.'''
		self.handlePrivate(sentence, output)

	def handlePrivate(self, sentence, output):
		'''Run output through the default handling process. Shouldn't be called 
		externally. Default implementation first does class specific handling,
		second script handling and last default handlers.'''
		self.handle(sentence, output)
		self.handleScript(sentence, output)
		self.handlers.handle(sentence, output)
		
	def getAddress(self):
		if self.address == None:
			if self.owner == None:
				return self.__class__.__name__
			else:
				try:
					s = self.location.getAddress()
				except AttributeError:
					s = self.owner.getAddress()
				return s + ':' + self.__class__.__name__
		else:
			return self.address
			
	def getScript(self):
		return 
		if self.address == None:
			self.address = self.getAddress()

		return self.ownerGame.script.getNode(self.address)
			
	def handle(self, sentence, output):
		pass
		
	def handleScript(self, sentence, output):
		pass
		
class HandlerAccess:
	'''Container for handler functions.'''
	close = True
	
	def __init__(self, parent):
		self.parent = parent
		self.handlers = {}
		
	def XMLSetup(self, node):
		for n in node.children:
			if n.node.nodeName == 'response':
				if n.node.getAttribute('sentence'):
					self.handlers[n.node.getAttribute('sentence')] = n.getValue()
	
	def handle(self, sentence, output):
		for handler in self.handlers:
			if sentence == handler:
				output.write(self.handlers[handler], self.close)

	def __setitem__(self, name, value):
		'''Set new handler.
		
		name : str - Compared to sentence.
		value : callable / function / str - Called with output as the only argument.
		String is looked up in the item dictionary and called with output as the only 
		argument.'''
		if name not in self.handlers:
			self.handlers[name] = value
		else:
			raise HandlerException("Handler for input '%s' already exists" % name)
			
	def __getitem__(self, name):
		'''Get handler.
		
		name : str'''
		if name not in self.handlers:
			raise HandlerException("Handler for input %s already exists" % name)
		else:
			return self.handlers[name]
			
	def __delitem__(self, name):
		'''Delete handler.
		
		name : str'''
		self.handlers.__delitem__(name)
			
	def __iter__(self):
		'''Iterate through handler sentences.'''
		return iter(self.handlers)
			
	def __contains__(self, other):
		'''Compares all handler names to other.'''
		for handler in self:
			if other == handler:
				return True
				
		return False
		
class HandlerEvent:
	def __init__(self, type, output):
		self.type = type
		self.output = output

def validateHandlerFunction(function):
	'''Make sure handler function can be pickled. Raise HandlerException otherwise.'''
	return
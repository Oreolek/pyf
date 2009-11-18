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
		self.owner = getattr(self, 'owner', None)
		'''Owner of this object in the game world.'''
		
		self.responses = self.responses.copy()
		'''Instantiated into a Responses object after object initiation.'''
		
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
		"""Set up any user defined variables for item. Default implementation 
		does nothing."""
		pass
		
	def initFromScriptNode(self, node, dict):
		pass
		
	@property
	def ownerGame(self):
		'''@rtype	:	Game'''
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
			
		@type 	output:	Output
		@param	output:	Output instance to associate with this event.'''
		
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
		cls.listeners[type].insert(0, function)

	def addEventListener(self, type, handler):
		'''Add event listener.
		
		@type	type:		str
		@param	type:		ID of the event type to listen to.
		
		@type	handler	:	tuple
		@param	handler	:	[:-1] Arguments to pass to handler function when event is
							fired.
							[-1] The actual handler function.'''
		validateHandlerFunction(handler[1])
			
		if type not in self.listeners:
			self.listeners[type] = []
			
		l = self.listeners[type]
			
		l.insert(0, handler)
		
	def removeEventListener(self, type, handler):
		'''Remove event listener.
		
		@type	type:		str
		@param	type:		Event ID.
		
		@type	handler:	tuple
		@param	handler:	The same tuple that was used to add the event listener.'''
		self.listeners[type].remove(handler)
	
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
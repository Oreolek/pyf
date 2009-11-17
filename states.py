"""Game states used for handling player input."""

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

import utils, lib
from errors import *

class State:
	'''Base class.'''
	request = ">"
	
	def __init__(self, actor):
		self.actor = actor
		if hasattr(self.actor, 'state'):
			self.oldState = self.actor.state
	
	def handle(self, sentence, output):
		raise StateError("Handler function undefined.")
	
	def __eq__(self, other):
		if other == self.__class__:
			return True
		return False
			
	def __ne__(self, other):
		return self.__eq__(other)*-1+1 == True
		
	def restoreState(self):
		self.actor.state = self.oldState
		
	def handleTimedEvents(self, sentence, output):
		return self.oldState.handleTimedEvents(sentence, output)

class Running(State):
	timedEvents = []
	
	def handle(self, sentence, output):
		try:
			actor = self.actor
			actor.intHandle(sentence, output)
			for word in sentence.nouns:
				item = word.item
				if actor.canAccess(item):
					item.intHandle(sentence, output)
						
			actor.owner.intHandle(sentence, output)
			actor.ownerGame.intHandle(sentence, output)
			handled = False
		except OutputClosed:
			handled = True
			
		timed = self.handleTimedEvents(sentence, output)
		if not handled and not timed:
			try:
				actor.unhandledSentence(sentence, output)
				raise GameError("Sentence %s wasn't handled" % str(sentence))
			except OutputClosed:
				pass
	
	def handleTimedEvents(self, sentence, output):
		l = self.timedEvents
		self.timedEvents = []
		handled = False
		for event in l:
			output.open()
			try:
				event.handle(sentence, output)
			except OutputClosed, e:
				handled = True
				
			if not event.done:
				self.timedEvents.append(event)
		
		return handled
		
class Disambiguation(State):
	def __init__(self, actor, error):
		State.__init__(self, actor)
		self.words = error.words
		self.sentence = error.sentence
		self.matches = error.matches
		
	def handle(self, sentence, output):
		found = None
		for match in self.words:
			word = match.word
			if word == sentence.s:
				found = match
				
		if found:
			self.resumeMatching(match)
			output.write('(%s)' % word.name, False)
			self.oldState.handle(self.sentence, output)
		else:
			self.oldState.handle(sentence, output)
			
		self.restoreState()
		
	def tryResolve(self):
		l = []
		for match in self.words:
			if type(match.word) == lib.Noun:
				if match.word in self.sentence.actor.pronouns.values():
					if self.sentence.actor.canAccess(match.word.item):
						l = [match]
						break
				elif self.actor.canAccess(match.word.item):
					l.append(match)
			else:
				raise DisambiguationError("Can't resolve %s - only nouns can be ambiguous." % str(match.word))
				
		self.words = l
		return self.resolved()
		
	def resolved(self):
		if len(self.words) == 1:
			return True
		elif len(self.words) == 0:
			raise DisambiguationError("None of the matches are possible")
		else:
			return False
			
	def specifyObject(self, output):
		pass
			
	def resumeMatching(self, match):
		self.matches.insert(0, match)
		self.sentence.applyMatches(self.matches)
		self.restoreState()
	
	def message(self):
		s = 'Which do you mean, '
		l = []
		for word in self.words:
			l.append(word.word.definite)
		s += utils.naturalJoin(l, ', ', ' or ')
		s += '?'
		
		return s
			
class Finished(State):
	def handle(self, sentence, output):
		raise StateError("Can't handle input - the game has ended.")
		
class Talking(State):
	request = "?"
	def __init__(self, actor, npc):
		State.__init__(self, actor)
		self.npc = npc
		
	def handle(self, sentence, output):
		if sentence == self.npc.ENDING:
			self.restoreState()
			output.write(self.npc.responses[self.npc.CONVERSATION_ENDED], False)
		else:
			try:
				self.npc.converseAbout(sentence, output)
			except OutputClosed:
				pass
		
class Question(State):
	request = "?"
	INVALID_ANSWER = "questionInvalidAnswer"
	responses = {
		INVALID_ANSWER: "I'm not sure what that means."
	}
	
	def __init__(self, actor, handler):
		State.__init__(self, actor)
		self.handler = handler
		
	def handle(self, sentence, output):
		try:
			self.handler(sentence, output)
		except OutputClosed:
			self.restoreState()
		finally:
			output.write(self.responses[self.INVALID_ANSWER])
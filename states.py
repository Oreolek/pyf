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
	
	def __init__(self, game):
		self.game = game
		self.oldState = self.game.state
	
	def handle(self, sentence, output):
		raise StateError("Handler function undefined.")
	
	def __eq__(self, other):
		if other == self.__class__:
			return True
		return False
			
	def __ne__(self, other):
		return self.__eq__(other)*-1+1 == True
		
	def restoreState(self):
		self.game.setState(self.oldState)

class Running(State):
	def handle(self, sentence, output):
		self.game.s = sentence
		
		try:
			self.game.actor.intHandle(sentence, output)
			for word in sentence:
				if type(word) == lib.Noun:
					item = word.item
					if self.game.actor.canAccess(item):
						item.intHandle(sentence, output)
						
			self.game.actor.owner.intHandle(sentence, output)
			self.game.handlePrivate(sentence, output)
		except OutputClosed:
			pass
			
class Disambiguation(State):
	def __init__(self, game, error):
		State.__init__(self, game)
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
				if self.game.actor.canAccess(match.word.item):
					l.append(match)
			else:
				raise Excepion("Can't resolve %s - only nouns can be ambiguous." % str(match.word))
				
				
		self.words = l
		return self.resolved()
		
	def resolved(self):
		if len(self.words) == 1:
			return True
		elif len(self.words) == 0:
			import pdb
			pdb.set_trace()
		else:
			return False
			
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
	def __init__(self, game, npc):
		State.__init__(self, game)
		self.npc = npc
		
	def handle(self, sentence, output):
		if sentence == self.npc.ENDING:
			self.end()
			output.write(self.npc.responses[self.npc.CONVERSATION_ENDED], False)
		else:
			try:
				self.npc.converseAbout(sentence, output)
			except OutputClosed:
				pass
		
	def end(self):
		self.game.setState(self.oldState)
		
class Question(State):
	request = "?"
	INVALID_ANSWER = "questionInvalidAnswer"
	responses = {
		INVALID_ANSWER: "I'm not sure what that means."
	}
	
	def __init__(self, game, handler):
		State.__init__(self, game)
		self.oldState = game.state
		self.handler = handler
		
	def handle(self, sentence, output):
		try:
			self.handler(sentence, output)
		except OutputClosed:
			self.restoreState()
		finally:
			output.write(self.responses[self.INVALID_ANSWER])
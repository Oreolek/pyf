
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
along with PyF.  If not, see <http://www.gnu.org/licenses/>."""

class PropError(Exception):
	pass
	
class ScriptError(Exception):
	pass
	
class ScriptChildError(Exception):
	pass
	
class OutputClosed(Exception):
	pass
	   

class OutputError(Exception):
	pass

class HandlerException(Exception):
	pass

class MatchingError(Exception):
	pass
	
class MoveError(Exception):
	pass

class AmbiguityError(Exception):
	def __init__(self, words, sentence, matches):
		Exception.__init__(self ,"Word \"%s\" matched by %i words" % (str(words[0].s), len(words)))
		self.sentence = sentence
		self.words = words
		self.matches = matches
		
class DisambiguationError(Exception):
	pass

class StateError(Exception):
	pass

class GameError(Exception):
	pass
	
class ScriptClassError(Exception):
	pass
	
class SkipHandle(Exception):
	pass
	
class InlineCodeError(Exception):
	pass
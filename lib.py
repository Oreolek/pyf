'''lib module holds all the classes used for parsing sentences in PyF.'''

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

from errors import *

class Lib(object):
	"""A collection of words that handles parsing sentences. Use standardlib.standardLib()
	to construct a Lib with the standard words."""
	
	words = []
	
	def __init__(self, *words):
		'''Create new Lib instance.
		
		*words : *Word - Words to append to library.'''
		self.words = []
		self.append(*words)
		
	def readScript(self, script):
		"""Read script nodes as synonyms. Unimplemented."""
	
	def remove(self, *words):
		"""Remove argument words from library."""
		for word in words:
			for i in range(0, len(self)):
				if self.words[i].eqString(word):
					del self.words[i]
					break
	
	def clear(self):
		"""Completely clears library of all words."""
		self.words = []
		
	def append(self, *words):
		"""Add argument *words to libary."""
		self.words.extend(words)
		
	def __iter__(self):
		"""Iterate through words in the lib."""
		return iter(self.words)
		
	def __len__(self):
		return len(self.words)
		
	def __str__(self):
		return '\n'.join(self.words)
		
	def parse(self, s):
		"""Parse a sentence based on the words in this library.
		
		s : string to parse
		
		returns : a parsed sentence"""
		sentence = Sentence(s) #
		sentence.lib = self
		s = sentence.s # clean string

		matches = []
		
		for word in self:
			match = word.containedIn(s)
			
			if match:
				matches.append(match)
		
		sentence.applyMatches(matches)

		return sentence
		
		
class Word(object):
	wildcards = []
	name = ''
	words = ()
	def __init__(self, *words):
		"""Construct Word with *words specified as synonyms.
		
		words : a list of strings or a list"""
		l = []
		for word in words:
			if isinstance(word, str):
				l.append(word)
			else:
				for w in word:
					l.append(w)
				
		words = l
		
		self.name = words[0]
		
		l = []
		for word in words:
			l.append(word.lower())
		
		l.extend(self.__class__.wildCards())
			
		self.sortWords(l)
		self.words = tuple(l)
	
	@classmethod
	def wildCards(cls):
		l = []
		for base in cls.__bases__:
			if base != Word and base != object:
				l.extend(base.wildCards())
		l.append('*' + cls.__name__.lower())
		return l
		
	def addWord(self, s):
		"""Add new synonym.
		
		s : str"""
		self.words = self.words+(s,)
	
	def removeWord(self, s):
		"""Remove synonym.
		
		s : str"""
		l = list(self.words)
		l.remove(s)
		self.words = tuple(l)
		
	def sortWords(self, l):
		"""Sort words according to length, longest to shortest."""
		l.sort()
		l.reverse()
		return l
		
	def __eq__(self, other):
		'''other : str / Word - If other is an Word instance, all of the words' are
		matched against each other. If other is a string, all synonyms are checked
		against the word.
		
		returns : bool'''
		if isinstance(other, str) or isinstance(other, unicode):
			return self.eqString(other)
		
		if issubclass(other.__class__, Word):
			for oword in other:
				if self.eqString(oword):
					return True
		
		return False
		
	def __ne__(self, other):
		return self.__eq__(other)*-1+1 == True
			
	def __iter__(self):
		"""Iterate through every synonym of Word."""
		return iter(self.words)
		
	def containedIn(self, s):
		"""Checks if string s contains the word.
		
		s : string
		
		returns : Match object or None if failed"""
		for word in self:
			try:
				return self.matchString(word, s)
			except MatchingError:
				continue
						
	def matchString(self, word, s):
		"""Checks if string s contains word.
		
		word : string
		s : string
		
		returns : Match instance"""
		return Match(word,s,self)

	def __str__(self):
		return self.name
		
	def eqString(self, s):
		"""Matches every synonym against string s."""
		for word in self:
			if word == s:
				return True
				
		return False
		
class Verb(Word):
	pass
class Touch(Verb):
	pass
class Attack(Verb):
	pass
class Move(Touch):
	pass
class Social(Verb):
	pass
class Answer(Social):
	pass
class Direction(Word):
	pass
	
class Noun(Word):
	def __init__(self, *words):
		Word.__init__(self, *words)
		self.adjective = None
		self.item = None
		
		# use Python's str.istitle to figure out if name is a title
		if self.name.istitle():
			self.definite = self.name
		else:
			self.definite = "the %s" % self.name
	
		if self.name[-1] == 's': # assume that the name is plural
			self.indefinite = 'some %s' % self.name
		else:
			self.indefinite = None
			for consonant in consonants:
				if self.name.startswith(consonant):
					self.indefinite = 'a %s' % self.name
					break
				
			if self.indefinite == None:
				self.indefinite = 'an %s' % self.name
		
		
	def matchString(self, word, s):
		"""Recursive function for matching argument word and all Noun instance's
		adjectives against argument s. 
		
		word : string
		s : string
		
		returns : Match instance or None if failed"""
		if self.adjective == None:
			return Word.matchString(self, word, s)

		else:
			match = Match(word, s, self)

			for a in self.adjective:
				newWord = a+' '+word # construct new string prefixed with an adjective
				try:
					return self.matchString(newWord, s) # match new string
				except MatchingError:
					continue
					
			return match
				
			
	def __eq__(self, other):
		if type(other) == str:
			l = Lib()
			l.append(self)
			if self.adjective != None:
				l.append(self.adjective)
			s = l.parse(other)
			if len(s) == 1 and s[0] == self:
				return True
			else:
				return False
		else:
			return Word.__eq__(self, other)
	
class Location(Noun):
	pass
class Adjective(Word):
	pass
class Preposition(Word):
	pass
class Ignore(Word):
	pass
class Internal(Word):
	'''Reserved for keywords like "save", "load", "again".'''
class Unknown(Word):
	pass

class Sentence:
	def __init__(self, s):
		self.s = Sentence.sanitize(s)
		
		self.words = []
		self.appliedMatches = []
		
	@classmethod
	def sanitize(cls, s):
		'''Sanitize string s for parsing.'''
		s = s.lower()
		s = ' ' + s + ' '		
		
		while '  ' in s:
			s = s.replace('  ', ' ')
		s = s.replace(',','')
		s = s.replace('.','')
		
		return s
		
	def applyMatches(self, matches):
		"""Apply list of Match instances to sentence. 
		
		matches : list of Match instances"""
		
		def available(l, match):
			for matched in l: # go through all the matched words
				if matched.contradicts(match):
					return False
					
			return True
			
		matches.sort(key = lambda x: -len(x)) # sort from longest match to the shortest
		for i in range(0, len(matches)):
			if available(self.appliedMatches, matches[i]):
				l = []
				if matches[i].s[0] != '*':
					try:
						x = i
						while matches[x] == matches[i]:
							l.append(matches[x])
							x += 1
						
					except IndexError:
						pass
					
					if l != [matches[i]]:
						raise AmbiguityError(l, self, matches[i+len(l):])
					
				self.applyMatch(matches[i])
				
		# turn rest of the words into word instances
		singleWords = self.s.split(' ')
		for word in singleWords:
			if word != '': # ignore empty strings in the beginning and end
				u = Unknown(word)
				u.removeWord('*unknown')
				if word[0] == '*':
					u.addWord(word)
				match = Match(word, self.s, u)
				if available(self.appliedMatches, match):
					self.applyMatch(match) 
				
		self.finalize()
		
	def applyMatch(self, match):
		'''Apply match object to word list and record the change into self.appliedMatches.'''
		self.words.append(match)
		self.appliedMatches.append(match)
		
		self.words.sort(key = lambda i: i.x)
		
	def finalize(self):
		"""Finalize word list - turn match instances into words."""
		l = []
		for word in self.words:
			l.append(word.word)
		self.words = tuple(l)
		
	def __str__(self):
		s = ''
		for word in self.words:
			s += str(word) + ' '
		return s[:-1]
		
	def __len__(self):
		'''returns : int - The length of current word list. Unfinalized instances always
		return 0.'''
		return len(self.words)
		
	def __getitem__(self, i):
		'''i : int
		
		returns : Word - Returns the word at index i in the current word list. '''
		return self.words[i]
		
	def __iter__(self):
		'''returns : iterator - Returns an iterator object for looping through all
		Word instances in the word list.'''
		return iter(self.words)
		
	def parseString(self, s):
		'''Parse string into a Sentence according to the words in the word list.
		
		s : str
		
		returns : Sentence'''
		l = Lib()
		for word in self.words:
			l.append(word)
			
		s = l.parse(s)
		self.comp = s
		return s
		
	def __eq__(self, other):
		'''other : str / Sentence - Parses strings into a sentence according to the 
		word list. Sentence is matched by matching all Words against each other, skipping
		Ignored words. Raises Exception if trying to compare to other objects.'''
		if type(other) == str or type(other) == unicode:
			other = self.parseString(other)
		elif issubclass(other.__class__, Word):
			if len(self) != 1:
				return False
			else:
				return other == self[0]
		elif issubclass(other.__class__, Sentence):
			other = other.words
		
		x, y = 0, 0
		for i in range(0, min(len(self), len(other))):
			skip = False
			while issubclass(other[i+x].__class__, Ignore):
				x += 1

			while issubclass(self[i+y].__class__, Ignore):
				y += 1
			
			if self[i+y] != other[i+x]:
				return False
				
		if i+x != len(other)-1 or i+y != len(self)-1:
			return False

		return True
		
	def __ne__(self, other):
		return self.__eq__(other)*-1+1 == True
		
	def __getslice__(self, start, end):
		'''Create a new sentence with the words from the slice.'''
		sentence = Sentence(self.s)
		sentence.words = self.words[start:end]
		return sentence
		
	def __contains__(self, other):
		'''Match all words in the word list against other.
		
		other - str / Word
		
		returns : bool'''
		for word in self:
			if word == other:
				return True
				
		return False
		
class Match:
	'''Used internally for matching strings in user input.'''
	def __init__(self, word, s, r):
		self.s = word
		word = ' '+word+' '
		self.word = r

		try:
			self.x = s.index(word) + 1
		except ValueError:
			raise MatchingError("Match not found.")
		self.length = len(word) - 2
		self.y = self.x + self.length
		
	def __nonzero__(self):
		if self.length == 0:
			return False
		else:
			return True
		
	def __len__(self):
		return self.length
		
	def contradicts(self, other):
		if self.x > other.x and self.x < other.y or self.y > other.x and self.y < other.y:
			return True
		elif self.x < other.x and self.y > other.y:
			return True
		elif self.x == other.x and self.y != other.y or self.y == other.y and self.x != other.y:
			return True
		else:
			return False
			
	def __eq__(self, other):
		if self.x == other.x and self.y == other.y:
			return True
		else:
			return False
		
consonants = (
	'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u'
)
#: matched against the word's beginning to get the article of the word

from standardlib import standardLib # included here for convenience
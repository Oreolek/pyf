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
		
	def __getitem__(self, name):
		for word in self:
			if word == name:
				return word
		
	def parse(self, sentence):
		"""Parse a sentence based on the words in this library.
		
		s : Sentence"""
		sentence.lib = self

		matches = []
		
		for word in self:
			if type(word) == Ignore:
				for word in word:
					sentence.s = sentence.s.replace(word + ' ', '')
		
		for word in self:
			match = word.containedIn(sentence.s)
			
			if match:
				matches.extend(match)
		
		sentence.applyMatches(matches)
		
		
class Word(object):
	'''Superclass for all words.'''
	name = ''
	words = ()
	def __init__(self, *words):
		"""Construct Word with *words specified as synonyms.
		
		words : a list of strings or a list"""
		
		if words:
			self.name = words
	
	@property
	def name(self): 
		if self.words:
			return self.words[0]
		else:
			return None

	@name.setter
	def name(self, value):
		self.setWords(value)
		
	def setWords(self, value):
		if value:
			words = value
			l=[]
			for word in words:
				if type(word) in (str, unicode):
					l.append(word)
				else:
					for w in word:
						l.append(w)

			for word in l:
				s = word
				s = s.replace('the ', '')
				s = s.replace('a ', '')
				s = s.replace('an ', '')
				if s != word:
					l.append(s)
			
			l.extend(self.__class__.wildcards())
			self.words = tuple(l)
		else:
			self.words = value

	@classmethod
	def wildcards(cls):
		l = []
		for base in cls.__bases__:
			if base != Word and base != object:
				l.extend(base.wildcards())
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
		l.sort(key = lambda x: len(x))
		l.reverse()
		return l
		
	def __eq__(self, other):
		'''other : str / Word - If other is an Word instance, all of the words' are
		matched against each other. If other is a string, all synonyms are checked
		against the word.
		
		returns : bool'''
		if type(other) in (str, unicode):
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
		l = []
		for word in self:
			l.extend(self.matchString(word, s))
		return l
						
	def matchString(self, word, s):
		"""Checks if string s contains word.
		
		word : string
		s : string
		
		returns : Match instance"""
		return matchWord(word,s,self)

	def __str__(self):
		return self.name
		
	def eqString(self, s):
		"""Matches every synonym against string s."""
		for word in self:
			if word == s:
				return True
				
		return False
	
	@property
	def isTitle(self):
		return self.name.istitle()
	
	@property
	def isPlural(self):
		if not self.isTitle:
			s = self.name.split(' of ')[0]
			if s.endswith('s'):
				return True
			else:
				return False
		
	@property
	def verbPlural(self):
		if not self.isTitle:
			return self.name.endswith('s')
		
class Verb(Word):
	'''Superclass for all verbs.'''
class CloseVerb(Verb):
	'''Used for verbs that require you to be close to something.'''
class Touch(CloseVerb):
	'''Used for verbs that require you to touch its object.'''
class Attack(Touch):
	'''Used for aggressive verbs that require you to attack object.'''
class Move(Touch):
	'''Used for verbs that attempt to move things.'''
class Social(CloseVerb):
	'''Used for verbs that attempt social interaction.'''
class SocialTouch(Touch, Social):
	'''Used for social touching verbs.'''
class Answer(Social):
	'''Used for verbs that answer NPC's questions.'''
class Direction(Word):
	'''Used for defining movement directions.'''
	
class Noun(Word):
	'''Superclass for all nouns.'''
	def __init__(self, *words):
		Word.__init__(self, *words)
		self.adjective = None
		self.item = None
		
	@property
	def name(self):
		if self.words:
			return self.words[0]
		else:
			return None
	
	@name.setter
	def name(self, value):
		self.setWords(value)
		
		if self.name:
			if self.isTitle:
				self.definite = self.name
			else:
				self.definite = "the %s" % self.name
	
			if self.isPlural: # assume that the name is plural
				self.indefinite = 'some %s' % self.name
			else:
				self.indefinite = None
				for consonant in consonants:
					if self.name.startswith(consonant):
						self.indefinite = 'a %s' % self.name
						break
				
				if self.indefinite == None:
					self.indefinite = 'an %s' % self.name
		else:
			self.definite = None
			self.indefinite = None
		
	def matchString(self, word, s):
		"""Recursive function for matching argument word and all Noun instance's
		adjectives against argument s. 
		
		word : string
		s : string
		
		returns : Match instance or None if failed"""
		if self.adjective == None:
			return Word.matchString(self, word, s)
		else:
			matches = matchWord(word, s, self)
			for match in matches:
				for a in self.adjective:
					newWord = a+' '+word # construct new string prefixed with an adjective
					match = self.matchString(newWord, s) # match new string
					if match:
						return match
						
			if matches:
				return [matches[0]]
			else:
				return matches
			
				
			
	def __eq__(self, other):
		if type(other) == str:
			l = Lib()
			l.append(self)
			if self.adjective != None:
				l.append(self.adjective)
			s = Sentence(other)
			l.parse(s)
			if len(s) == 1 and s[0] == self:
				return True
			else:
				return False
		else:
			return Word.__eq__(self, other)
	
class Location(Noun):
	'''Used for nouns that define physical locations in a room.'''
class Creature(Noun):
	'''Used for all living creatures.'''
class Person(Creature):
	'''Used for people.'''
class Animal(Creature):
	'''Used for animals.'''

class Adjective(Word):
	'''Superclass for all adjectives.'''
class Preposition(Word):
	'''Superclass for all prepositions.'''
class Ignore(Word):
	'''Words for the parser to ignore during parsing.'''
class Internal(Word):
	'''Reserved for keywords like "save", "load", "again".'''
class Unknown(Word):
	'''Instantiated for any words in the sentence that the parser doesn't understand.'''
	@classmethod
	def wildcards(cls):
		return []

class Sentence:
	'''Container object for word instances.'''
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
		
	@property
	def nouns(self):
		l = []
		for word in self:
			if word == '*noun':
				l.append(word)
		return l
		
	@property
	def verbs(self):
		l = []
		for word in self:
			if word == '*verb':
				l.append(word)
		
		return l
		
	def applyMatches(self, matches):
		"""Apply list of Match instances to sentence. 
		
		matches : list of Match instances"""
		
		def available(l, match):
			for matched in l: # go through all the matched words
				if matched.contradicts(match):
					return False
					
			return True
			
		self.matches = matches
			
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
				'''if word[0] == '*':
					u.addWord(word)'''
				match = Match(word, self.s, u, self.s.index(word)-1)

				# see if word hasn't been matched by a better word
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
			l.append(word.wordObject)
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
		
		s = Sentence(s)
		l.parse(s)
		return s
		
	def __eq__(self, other):
		'''other : str / Sentence - Parses strings into a sentence according to the 
		word list. Sentence is matched by matching all Words against each other, skipping
		Ignored words. Raises Exception if trying to compare to other objects.'''
		if type(other) in (str, unicode):
			other = self.parseString(other)
		elif issubclass(other.__class__, Word):
			if len(self) != 1:
				return False
			else:
				return other == self[0]
		elif issubclass(other.__class__, Sentence):
			other = other.words
		
		try:
			for x, y in self.iterSentences(other):
				if x != y:
					return False
		except MatchingError, e:
			return False
				
		return True
		
	def iterSentences(self, other):
		x, y = 0, 0
		for i in range(min(len(self), len(other))):
			try:
				while self[i+x].__class__ == Ignore:
					x += 1
				while other[i+y].__class__ == Ignore:
					y += 1
			except KeyError:
				raise MatchingError("Too short")

			yield self[i+x], other[i+y]
			
		if i+x+len(other) != i+y+len(self):
			raise MatchingError("Too long")
		
	def __ne__(self, other):
		return self.__eq__(other) == False
		
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

def matchWord(word, s, wordObject):
	w = ' %s ' % word
	e = []
	l = s.rsplit(w,1)
	while len(l) > 1:
		e.append(Match(word, s, wordObject, max(len(l[0])-1, 0)))
		l.pop()
		l[0] += ' '
		l = l[0].rsplit(w,1)
		
	return e
		
class Match(object):
	'''Used internally for matching strings in user input.'''
	def __init__(self, word, s, wordObject, index):
		self.s = word
		self.x = index
		self.wordObject = wordObject
		self.length = len(word)
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
		elif self.x == other.x or self.y == other.y:
			return True
		else:
			return False
			
	def __eq__(self, other):
		if self.x == other.x and self.y == other.y:
			return True
		else:
			return False
		
consonants = (
	'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'z'
)
'''matched against the word's beginning to get the article of the word'''
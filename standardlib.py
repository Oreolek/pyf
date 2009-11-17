'''Standard word definitions.'''

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

from lib import *

words = (
	Verb('go', 'walk'),
	Verb('enter'),
	Verb('exit'),
	Verb('examine', 'x', 'look at', 'l', 'look'),
	Move('take', 'get', 'pick up'),
	Move('drop'),
	Move('give'),
	Move('put', 'place'),
	Move('throw'),

	Touch('search'),

	Verb('set'),
	Touch('blow'),
	Verb('burn'),
	Touch('buy', 'purchase'),
	Touch('climb'),
	Verb('cut'),
	Touch('dig'),
	Touch('fill'),
	Verb('listen to', 'listen'),
	Touch('sit down on', 'sit down', 'sit'),
	Touch('lie down on', 'lie down'),

	SocialTouch('kiss'),
	SocialTouch('hug'),
	
	Attack('hit', 'punch'),
	Attack('kick'),
	Attack('assault', 'attack'),
	Attack('break'),

	Answer('agree to', 'yes'),
	Answer('disagree to','no'),
	Answer('apologize for', 'apologize', 'sorry'),

	Verb('pray'),
	Verb('think'),
	Verb('jump'),
	Verb('wake up'),
	Verb('wave'),

	Social('talk to', 'talk', 'speak to', 'speak with', 'speak'),
	Social('answer', 'reply'),
	Social('show'),

	Social('ask', 'question'),
	Social('tell', 'order', 'command'),
	Move('push'),
	Move('pull'),

	Touch('open'),
	Touch('close'),
	Touch('lock'),
	Touch('unlock'),

	Touch('dress', 'wear', 'put on'),
	Touch('strip', 'take off', 'remove'),
	Touch('drink', 'sip'),
	Touch('eat'),
	Touch('taste'),
	Touch('turn on', 'switch on'),
	Touch('turn off', 'switch off'),
	Move('turn', 'twist', 'move', 'switch'),
	Touch('touch', 'rub', 'feel'),
	Touch('wake'),

	Verb('wait', 'z'),

	Direction('east', 'e'),
	Direction('west', 'w'),
	Direction('south', 's'),
	Direction('north', 'n'),
	Direction('northeast', 'ne'),
	Direction('northwest', 'nw'),
	Direction('southeast', 'se'),
	Direction('southwest', 'sw'),
	Direction('up', 'u'),
	Direction('down', 'd'),
	Direction('in'),
	Direction('outside', 'out', 'exit'),

	Preposition('about'),
	Preposition('with', 'using'),
	Preposition('at'),
	Preposition('on'),
	Preposition('under'),
	Preposition('next to'),
	Preposition('to'),
	Preposition('inside'),
	Preposition('through'),
	Preposition('beside'),

	Internal('again', 'g'),
	Internal('save'),
	Internal('load'),
	Internal('help'),
	Internal('hint'),
	Internal('score'),
	Internal('transcript'),
	Internal('inventory', 'inv', 'i'),

	Ignore('a', 'an'),
	Ignore('the'),
	Ignore('your')
)

def standardLib():
	'''Return standard PyF library.'''
	l = Lib()
	l.append(*words)
	
	return l
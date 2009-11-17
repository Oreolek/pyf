
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

from pyf import states

def runGame(game):
	'''Run game on the terminal interface.'''
	print 'Type "quit" at any time to quit the game.'
	interface = TerminalInterface(game)
	interface.output(game.getIntro())
	while game.actor.state != states.Finished: # While the game is running
		input = raw_input(game.actor.state.request + ' ') # Get user input
		if input == 'quit': 
			break # Exit game 
		interface.input(input) # Pass player input to the game and print the output
		
def testGame(game, s):
	'''Test game with s. Run commands in s and print output.
	
	@type	game:	Game
	
	@type	s:		str
	@param	s:		A newline delimited string containing commands to run the game with.'''
	
	interface = TerminalInterface(game)
	for line in s.split('\n'):
		line = line.strip()
		if line:
			print game.actor.state.request + ' ' + line
			interface.input(line)
		
import cgi, re
		
class TerminalInterface:
	'''A basic command line interface for playing PyF games.'''
	
	replace = {'<br />': "\n", 
		'<br/>':"\n", 
		'<h4>': '-- ', 
		'</h4>': ' --', 
		'<h1>': '=== ',
		'</h1>': ' ===',}
	def __init__(self, game):
		self.game = game

	def input(self, s):
		self.output(self.game.input(s))
		
			
	def cleanOutput(self, s):
		p = re.compile(r'<.*?>')
	    
		for tag in self.replace:
			s = s.replace(tag, self.replace[tag])
		s = p.sub('', s)
		s = s.replace('\n ', '\n')
		return s.strip()
		
	def output(self, output):
		for line in output.lines:
			print self.cleanOutput(line)